import os

from langchain_google_genai import (ChatGoogleGenerativeAI,
                                    GoogleGenerativeAIEmbeddings)

from app.settings.config import settings
from app.utils.llm.base import LLMWrapper

os.environ["GOOGLE_API_KEY"] = settings.get("GOOGLE_API_KEY")


class Gemini(LLMWrapper):
    def __init__(self):
        self.model_version = "gemini-1.5-pro-latest"
        self.embedding_model = "models/embedding-001"
        self.google_api_key = settings.get("GOOGLE_API_KEY")
        self.dimensions = 768

    def get_llm(self):
        return ChatGoogleGenerativeAI(model=self.model_version)

    def load_embedding_model(self):
        return GoogleGenerativeAIEmbeddings(model=self.embedding_model)
