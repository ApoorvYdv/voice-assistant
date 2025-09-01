from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from src.core.workflows.voice_assistant import VoiceAssistantController

voice_assistant = APIRouter(
    prefix="/v1/voice-assistant",
    tags=["voice-assistant"],
)


@voice_assistant.post("/speech-to-text")
async def speech_to_text(
    controller: Annotated[VoiceAssistantController, Depends()],
    file: UploadFile = File(...),
):
    return await controller.speech_to_text(file)


@voice_assistant.get("/text-to-speech")
async def text_to_speech(
    text: str, controller: Annotated[VoiceAssistantController, Depends()]
):
    audio = await controller.text_to_speech(text)
    return StreamingResponse(
        audio,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=output.mp3"},
    )
