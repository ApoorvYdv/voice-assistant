from io import BytesIO

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from fastapi import File, HTTPException, UploadFile, status
from src.config.settings import settings


class VoiceAssistantController:
    def __init__(self):
        self.elevenlabs_client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

    async def speech_to_text(self, file: UploadFile = File(...)):
        """Transcribe the audio recording."""
        audio_data = await file.read()
        if not audio_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No audio data provided"
            )

        # Transcribe the audio file
        transcription = self.elevenlabs_client.speech_to_text.convert(
            file=audio_data,
            model_id="scribe_v1",  # Model to use, for now only "scribe_v1" is supported
            tag_audio_events=True,  # Tag audio events like laughter, applause, etc.
            language_code="eng",  # Language of the audio file. If set to None, the model will detect the language automatically.
            diarize=True,  # Whether to annotate who is speaking
        )
        return transcription

    async def text_to_speech(self, text: str):
        """Convert text to speech using ElevenLabs."""
        # Call text_to_speech API with turbo model for low latency
        response = self.elevenlabs_client.text_to_speech.stream(
            voice_id="pNInz6obpgDQGcFmaJgB",  # Adam pre-made voice
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_turbo_v2_5",
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
            ),
        )

        audio_stream = BytesIO()

        # write each chunk of audio data to the stream
        for chunk in response:
            if chunk:
                audio_stream.write(chunk)

        audio_stream.seek(0)

        return audio_stream
