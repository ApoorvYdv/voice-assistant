from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

from src.config.settings import settings
from src.core.nodes.calculator import CalculatorService
from src.core.nodes.news import NewsService
from src.core.nodes.weather import WeatherService
from src.utils.pretty_print_messages import pretty_print_messages


class SupervisorWorkflow:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            model="deepseek/deepseek-chat-v3-0324:free",
            base_url=settings.OPENROUTER_BASE_URL,
        )

    def get_news_agent(self):
        """news tool for fetching top 5 news headlines"""
        news_agent = create_react_agent(
            model=self.llm,
            tools=[NewsService().fetch_news],
            prompt=(
                "You are a news agent.\n\n"
                "INSTRUCTION:\n"
                "- Assist ONLY with news related tasks, only DONT do anything else\n"
                "- After you're done with your tasks, respond to the supervisor directly\n"
                "- Respond ONLY with the results of your work, don NOT include ANY other text"
            ),
            name="news_agent",
        )
        return news_agent

    def get_weather_agent(self):
        """weather tool for getting weather of the location"""
        weather_agent = create_react_agent(
            model=self.llm,
            tools=[WeatherService().fetch_weather_data],
            prompt=(
                "You are a weather agent.\n\n"
                "INSTRUCTION:\n"
                "- Assist ONLY with weather of a location related tasks, only DONT do any thing else\n"
                "- After you're done with your tasks, respond to the supervisor directly\n"
                "- Respond ONLY with the results of your work, do NOT include ANY other text"
            ),
            name="weather_agent",
        )
        return weather_agent

    def get_math_agent(self):
        """calculator app for doing addition, multiplication and division"""
        calculator_service = CalculatorService()
        math_agent = create_react_agent(
            model=self.llm,
            tools=[
                calculator_service.add,
                calculator_service.multiply,
                calculator_service.divide,
            ],
            prompt=(
                "You are a math agent.\n\n"
                "INSTRUCTIONS:\n"
                "- Assist ONLY with math-related tasks\n"
                "- After you're done with your tasks, respond to the supervisor directly\n"
                "- Respond ONLY with the results of your work, do NOT include ANY other text."
            ),
            name="math_agent",
        )
        return math_agent

    def supervisor(self):
        supervisor = create_supervisor(
            model=self.llm,
            agents=[
                self.get_math_agent(),
                self.get_weather_agent(),
                self.get_news_agent(),
            ],
            prompt=(
                "You are a supervisor managing three agents:\n"
                "- a weather agent. Assign weather for a location tasks to this agent\n"
                "- a math agent. Assign math-related tasks to this agent\n"
                "- a news agent. Assign news-related tasks to this agent\n"
                "Assign work to one agent at a time, do not call agents in parallel.\n"
                "Do not do any work yourself."
            ),
            add_handoff_back_messages=True,
            output_mode="full_history",
        ).compile()
        return supervisor

    def run(self):
        for chunk in self.supervisor().stream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "russia ukraine war?",
                    }
                ]
            }
        ):
            pretty_print_messages(chunk, last_message=True)

        final_message_history = chunk["supervisor"]["messages"]
