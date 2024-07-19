from typing import List, Union, Optional, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel


class ChatInputType(BaseModel):
    input: List[Union[HumanMessage, AIMessage, SystemMessage]]

class GenerativeUIState(TypedDict, total=False):
    input: HumanMessage
    model_name: str
    result: Optional[str]
    """Plain text response if no tool was used."""
    tool_calls: Optional[List[dict]]
    """A list of parsed tool calls."""
    tool_result: Optional[dict]
    """The result of a tool call."""