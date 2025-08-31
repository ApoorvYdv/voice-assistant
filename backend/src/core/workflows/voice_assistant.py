import uuid

import numpy as np
import sounddevice as sd
import whisper
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, MessagesState, StateGraph
from scipy.io.wavfile import write
from src.config.settings import settings
from backend.src.core.workflows.supervisor import SupervisorWorkflow


class VoiceAssistantState(MessagesState):
    """
    Represents the state of our voice assistant graph.

    Attributes:
        messages: The list of messages exchanged in the conversation.
        audio_stream: A list of audio bytes for the TTS response.
    """

    audio_stream_iterator: object


class VoiceAssistantWorkflow:
    def __init__(self):
        self.thread_id = str(uuid.uuid4())
        self.config = {
            "configurable": {"user_id": "Jarvis", "thread_id": self.thread_id}
        }

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", api_key=settings.GEMINI_API_KEY
        )
        self.elevenlabs_client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        self.supervisor = SupervisorWorkflow().supervisor()

    def _call_supervisor(self, state: VoiceAssistantState):
        """Invokes the compiled supervisor graph with the current state."""
        print("\nCalling Supervisor...")
        response = self.supervisor.invoke(state, config=self.config)
        print("Supervisor finished.")
        # Merge supervisor's messages into the existing state
        state["messages"] = response["messages"]
        return state

    def _record_audio(self, state: VoiceAssistantState):
        """Records audio from the microphone until Enter is pressed, then saves it to a .wav file."""
        # Recording Settings
        fs = 44100  # Sample rate
        duration = 5  # Recording duration in seconds
        audio_filename = "output.wav"

        print("--- Recording ---")
        print(f"Recording for {duration} seconds... Please speak now.")

        # Record audio from the default microphone
        # The recording is stored as a NumPy array
        recording = sd.rec(
            int(duration * fs), samplerate=fs, channels=1, dtype=np.int16
        )
        sd.wait()  # Wait until the recording is finished

        print("Recording finished.")

        # Save the recording as a WAV file
        write(audio_filename, fs, recording)
        print(f"Audio saved to '{audio_filename}'")
        print("-" * 20)

        # --- Step 3: Transcribe the Recording ---

        # Load the Whisper model.
        model = whisper.load_model("tiny")

        # Transcribe the audio file
        transcription = model.transcribe(audio_filename, fp16=False)

        # Write to messages
        return {"messages": [HumanMessage(content=transcription["text"])]}

    def _play_audio(self, state: VoiceAssistantState):
        """Plays the audio response from the remote graph with ElevenLabs."""

        # Response from the agent
        response = state["messages"][-1]

        # Prepare text by replacing ** with empty strings
        # These can cause unexpected behavior in ElevenLabs
        cleaned_text = response.content.replace("**", "")

        # Call text_to_speech API with turbo model for low latency
        audio_iterator = self.elevenlabs_client.text_to_speech.convert(
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

        # store the raw audio stream in the state to return
        return {"audio_stream_iterator": audio_iterator}

    def _build_workflow(self):
        graph = StateGraph(VoiceAssistantState)

        graph.add_node("supervisor", self._call_supervisor)
        graph.add_node("audio_output", self._play_audio)

        graph.add_edge(START, "supervisor")
        graph.add_edge("supervisor", "audio_output")
        graph.add_edge("audio_output", END)

        return graph.compile()
