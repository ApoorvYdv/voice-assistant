from typing import Annotated

from fastapi import APIRouter, Depends
from src.core.workflows.voice_assistant import VoiceAssistantWorkflow

voice_assistant = APIRouter(
    prefix="/v1/voice-assistant",
    tags=["voice-assistant", "text-to-speech", "speech-to-text"],
)


@voice_assistant.post("/tts")
async def text_to_speech(
    request: str, workflow: Annotated[VoiceAssistantWorkflow, Depends()]
):
    return await workflow.text_to_speech(request)
