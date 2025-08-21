import io
import threading
import uuid

import numpy as np
import sounddevice as sd
from elevenlabs import VoiceSettings, play
from elevenlabs.client import ElevenLabs
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph
from scipy.io.wavfile import write

from src.config.settings import settings
from src.core.workflows.supervisor_agent import SupervisorWorkflow


class VoiceAssistantWorkflow:
    def __init__(self):
        self.thread_id = str(uuid.uuid4())
        self.llm = ChatOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            model="deepseek/deepseek-chat-v3-0324:free",
            base_url=settings.OPENROUTER_BASE_URL,
        )
        self.elevenlabs_client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        self.supervisor = SupervisorWorkflow().supervisor()

    def _call_supervisor(self, state: MessagesState):
        """Invokes the compiled supervisor graph with the current state."""
        print("\nCalling Supervisor...")
        response = self.supervisor.invoke(state, config=self.config)
        print("Supervisor finished.")
        return {"messages": response["messages"]}

    def _record_audio_until_stop(self, state: MessagesState):
        """Records audio from the microphone until Enter is pressed, then saves it to a .wav file."""

        audio_data = []  # List to store audio chunks
        recording = True  # Flag to control recording
        sample_rate = 16000  # (kHz) Adequate for human voice frequency

        def record_audio():
            """Continuously records audio until the recording flag is set to False."""
            nonlocal audio_data, recording
            with sd.InputStream(
                samplerate=sample_rate, channels=1, dtype="int16"
            ) as stream:
                print("Recording your instruction! ... Press Enter to stop recording.")
                while recording:
                    audio_chunk, _ = stream.read(1024)  # Read audio data in chunks
                    audio_data.append(audio_chunk)

        def stop_recording():
            """Waits for user input to stop the recording."""
            input()  # Wait for Enter key press
            nonlocal recording
            recording = False

        # Start recording in a separate thread
        recording_thread = threading.Thread(target=record_audio)
        recording_thread.start()

        # Start a thread to listen for the Enter key
        stop_thread = threading.Thread(target=stop_recording)
        stop_thread.start()

        # Wait for both threads to complete
        stop_thread.join()
        recording_thread.join()

        # Stack all audio chunks into a single NumPy array and write to file
        audio_data = np.concatenate(audio_data, axis=0)

        # Convert to WAV format in-memory
        audio_bytes = io.BytesIO()
        write(
            audio_bytes, sample_rate, audio_data
        )  # Use scipy's write function to save to BytesIO
        audio_bytes.seek(0)  # Go to the start of the BytesIO buffer
        audio_bytes.name = "audio.wav"  # Set a filename for the in-memory file

        # Transcribe via Whisper
        transcription = self.llm.audio.transcriptions.create(
            model="whisper-1",
            file=audio_bytes,
        )

        # Print the transcription
        print("Here is the transcription:", transcription.text)

        # Write to messages
        return {"messages": [HumanMessage(content=transcription.text)]}

    def _play_audio(self, state: MessagesState):
        """Plays the audio response from the remote graph with ElevenLabs."""

        # Response from the agent
        response = state["messages"][-1]

        # Prepare text by replacing ** with empty strings
        # These can cause unexpected behavior in ElevenLabs
        cleaned_text = response.content.replace("**", "")

        # Call text_to_speech API with turbo model for low latency
        response = self.elevenlabs_client.text_to_speech.convert(
            voice_id="pNInz6obpgDQGcFmaJgB",  # Adam pre-made voice
            output_format="mp3_22050_32",
            text=cleaned_text,
            model_id="eleven_turbo_v2_5",
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
            ),
        )

        # Play the audio back
        play(response)

    def _build_workflow(self):
        graph = StateGraph(MessagesState)

        graph.add_node("audio_input", self._record_audio_until_stop)
        graph.add_node("supervisor", self._call_supervisor)
        graph.add_node("audio_output", self._play_audio)

        graph.add_edge(START, "audio_input")
        graph.add_edge("audio_input", "supervisor")
        graph.add_edge("supervisor", "audio_output")
        graph.add_edge("audio_output", END)

        return graph.compile()
