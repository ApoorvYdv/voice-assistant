import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from app.core.models.schemas import ChatInputType
from dotenv import load_dotenv
from app.core.controllers.chatbot_graph_controller import ChatbotGraph
load_dotenv()

description = """
Langchain with GenUI
"""

app = FastAPI(
    title="Gen UI App",
    description=description,
    version="0.0.1",
    # openapi_tags=tags_metadata,
    responses={404: {"description": "Not found"}},
)


origins = os.getenv("ALLOWED_ORIGINS") or []

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Access-Control-Allow-Headers",
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Origin",
    ],
)


graph = ChatbotGraph.create_graph()

runnable = graph.with_types(input_type = ChatInputType, output_type=dict)


add_routes(app, runnable, path="/chat", playground_type="chat")
