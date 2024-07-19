import os

from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings

from app.utils.llm.base import LLMWrapper
from app.settings.config import settings


class HuggingFace(LLMWrapper):
    def __init__(self):
        self.model_version = settings.get("HUGGING_FACE_EMBEDDINGS_MODEL_NAME")
        self.embedding_model = "models/embedding-001"
        self.huggingfacehub_api_token = settings.get("HUGGING_FACE_TOKEN")
        self.dimensions = 384

    def load_embedding_model(self):
        return HuggingFaceEndpointEmbeddings(
            model=self.model_version,
            huggingfacehub_api_token=self.huggingfacehub_api_token,
        )
