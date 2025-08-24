import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # firecrawl
    FIRECRAWL_API_KEY: str

    # open router
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str

    # grok
    GROK_API_KEY: str

    # gemini
    GEMINI_API_KEY: str

    # open weather map
    OPENWEATHERMAP_API_KEY: str

    # ask news
    ASKNEWS_CLIENT_ID: str
    ASKNEWS_CLIENT_SECRET: str

    # news api
    NEWS_API_KEY: str

    # langsmith
    LANGSMITH_TRACING: bool
    LANGSMITH_API_KEY: str
    LANGSMITH_ENDPOINT: str
    LANGSMITH_PROJECT: str

    # Eleven labs
    ELEVENLABS_API_KEY: str

    class Config:
        env_file = ".env"

    def model_post_init(self, __context) -> None:
        """Set up LangSmith environment variables after model initialization."""
        if self.LANGSMITH_TRACING:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = self.LANGSMITH_API_KEY
            os.environ["LANGCHAIN_ENDPOINT"] = self.LANGSMITH_ENDPOINT
            os.environ["LANGCHAIN_PROJECT"] = self.LANGSMITH_PROJECT


settings = Settings()
