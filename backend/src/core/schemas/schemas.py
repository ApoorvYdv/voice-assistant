from typing import Annotated, Any, Optional

from langgraph.graph.message import add_messages
from pydantic import BaseModel


class CompanyAnalysis(BaseModel):
    """Structured output for LLM company analysis focused on developer tools"""

    pricing_model: str  # Free, Freemium, Paid, Enterprise, Unknown
    is_open_source: Optional[bool] = None
    tech_stack: list[str] = []
    description: str = ""
    api_available: Optional[bool] = None
    language_support: list[str] = []
    integration_capabilities: list[str] = []


class CompanyInfo(BaseModel):
    name: str
    description: str
    website: str
    pricing_model: Optional[str] = None
    is_open_source: Optional[bool] = None
    tech_stack: list[str] = []
    competitors: list[str] = []
    # Developer-specific fields
    api_available: Optional[bool] = None
    language_support: list[str] = []
    integration_capabilities: list[str] = []
    developer_experience_rating: Optional[str] = None  # Poor, Good, Excellent


class ResearchState(BaseModel):
    query: str
    extracted_tools: list[str] = []  # Tools extracted from articles
    companies: list[CompanyInfo] = []
    search_results: list[dict[str, Any]] = []
    analysis: Optional[str] = None
