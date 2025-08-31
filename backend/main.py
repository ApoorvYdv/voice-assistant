import io

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from src.core.workflows.voice_assistant import VoiceAssistantWorkflow

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextInput(BaseModel):
    message: str


@app.post("/invoke-assistant")
async def invoke_assistant(input_data: TextInput):
    print(input_data.message)

    final_state = (
        VoiceAssistantWorkflow()
        ._build_workflow()
        .invoke({"messages": [HumanMessage(content=input_data.message)]})
    )
    print(final_state)

    audio_bytes_list = final_state["audio_stream"]
    audio_bytes = b"".join(audio_bytes_list)

    return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
