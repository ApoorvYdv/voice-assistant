from typing import Any
from app.core.models.schemas import GenerativeUIState

from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph
from app.utils.llm.factory import LLMFactory

from app.utils.tools.github_repo import github_repo
from app.utils.tools.weather_data import weather_data 
from app.utils.tools.invoice_parser import invoice_parser 

class ChatbotGraph:
    def __init__(self, model_name) -> None:
        self.llm = LLMFactory().get_llm_class(model_name)
        self.workflow = StateGraph(GenerativeUIState)

        self.workflow.add_node("invoke_model", self.invoke_model)
        self.workflow.add_node("invoke_tools", self.invoke_tools)
        self.workflow.add_conditional_edges("invoke_model", self.invoke_tools_or_return)
        self.workflow.set_entry_point("invoke_model")
        self.workflow.set_finish_point("invoke_tools")
        
        self.graph = self.workflow.compile()

    def create_graph(self) -> CompiledGraph:
        return self.graph
    
    def invoke_model(self, state: GenerativeUIState, config: RunnableConfig) -> GenerativeUIState:
        tools_parser = JsonOutputToolsParser()
        initial_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant. You're provided a list of tools, and an input from the user.\n"
                    + "Your job is to determine whether or not you have a tool which can handle the users input, or respond with plain text.",
                ),
                MessagesPlaceholder("input"),
            ]
        )

        tools = [github_repo, invoice_parser, weather_data]
        model_with_tools = self.llm.bind_tools(tools)
        chain = initial_prompt | model_with_tools
        result = chain.invoke({"input": state["input"]}, config)

        if not isinstance(result, AIMessage):
            raise ValueError("Invalid result from model. Expected AIMessage.")

        if isinstance(result.tool_calls, list) and len(result.tool_calls) > 0:
            parsed_tools = tools_parser.invoke(result, config)
            return {"tool_calls": parsed_tools}
        else:
            return {"result": str(result.content)}

    def invoke_tools(self, state: GenerativeUIState) -> GenerativeUIState:
        tools_map = {
            "github-repo": github_repo,
            "invoice-parser": invoice_parser,
            "weather-data": weather_data,
        }

        if state["tool_calls"] is not None:
            tool = state["tool_calls"][0]
            selected_tool = tools_map[tool["type"]]
            return {"tool_result": selected_tool.invoke(tool["args"])}
        else:
            raise ValueError("No tool calls found in state.")


    def invoke_tools_or_return(self, state: GenerativeUIState) -> str:
        if "result" in state and isinstance(state["result"], str):
            return END
        elif "tool_calls" in state and isinstance(state["tool_calls"], list):
            return "invoke_tools"
        else:
            raise ValueError("Invalid state. No result or tool calls found.")


