from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.settings.config import settings
from app.utils.llm.base import LLMWrapper


class OpenAI(LLMWrapper):
    def __init__(self):
        self.model_version = "gpt-4-turbo"
        self.embedding_model = "text-embedding-ada-002"
        self.dimensions = 1536
        self.api_key = settings.get("OPENAI_API_KEY")

    def get_llm(self):
        return ChatOpenAI(model=self.model_version, api_key=self.api_key)

    def load_embedding_model(self):
        return OpenAIEmbeddings(model=self.embedding_model, api_key=self.api_key)
