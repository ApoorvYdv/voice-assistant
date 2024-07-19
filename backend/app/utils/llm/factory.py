from app.utils.llm.gemini import Gemini
from app.utils.llm.groq import Groq
from app.utils.llm.ollama import OllamaLLM
from app.utils.llm.openai import OpenAI
from app.utils.llm.hugging_face import HuggingFace


class LLMFactory(object):
    def get_llm_class(self, model_name):
        default_class = {
            "openai": OpenAI,
            "gemini": Gemini,
            "groq": Groq,
            "ollama": OllamaLLM,
            "hugging_face": HuggingFace
        }
        return default_class.get(model_name)

    def build(self, model_name):
        llm_class = self.get_llm_class(model_name)
        return llm_class()
