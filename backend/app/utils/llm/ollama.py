from langchain_community.llms import Ollama
from langchain_experimental.graph_transformers import LLMGraphTransformer

from app.utils.llm.base import LLMWrapper


class OllamaLLM(LLMWrapper):
    def __init__(self):
        self.model_version = "llama3"

    def get_llm(self):
        return Ollama(model=self.model_version)

    def load_embedding_model(self):
        NotImplementedError
