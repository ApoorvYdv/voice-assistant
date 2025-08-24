from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from src.config.settings import settings
from src.core.tools.firecrawl import FirecrawlService
from src.core.prompts.prompts import DeveloperToolsPrompts
from src.core.schemas.schemas import CompanyAnalysis, CompanyInfo, ResearchState


class Workflow:
    def __init__(self):
        self.firecrawl = FirecrawlService()
        self.prompts = DeveloperToolsPrompts()
        self.llm = ChatOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            model="deepseek/deepseek-chat-v3-0324:free",
            base_url=settings.OPENROUTER_BASE_URL,
        )
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        graph = StateGraph(ResearchState)

        # node
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)

        # entry point
        graph.set_entry_point("extract_tools")

        # edges
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)

        return graph.compile()

    def _extract_tools_step(self, state: ResearchState) -> dict[str, Any]:
        print(f"🔎 Finding articles about {state.query}")

        article_query = f"{state.query} tools comparison best alternatives"
        search_results = self.firecrawl.search_companies(
            query=article_query, num_results=3
        )

        all_content = ""
        for result in search_results.data:
            url = result.get("url", "")
            scraped = self.firecrawl.scrape_company_page(url=url)
            if scraped:
                all_content + scraped.markdown[:1500] + "\n\n"

        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(
                content=self.prompts.tool_extraction_user(state.query, all_content)
            ),
        ]

        try:
            response = self.llm.invoke(messages)
            tool_names = [
                name.strip()
                for name in response.content.strip().split("\n")
                if name.strip()
            ]
            print(f"Extracted tools: {', '.join(tool_names)}")
            return {"extracted_tools": tool_names}
        except Exception as e:
            print(e)
            return {"extracted_tools": []}

    def _analyze_company_content(
        self, company_name: str, content: str
    ) -> CompanyAnalysis:
        structured_llm = self.llm.with_structured_output(CompanyAnalysis)

        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(
                content=self.prompts.tool_analysis_user(
                    company_name=company_name, content=content
                )
            ),
        ]

        try:
            analysis = structured_llm.invoke(messages)
            return analysis
        except Exception as e:
            print(e)
            return CompanyAnalysis(
                pricing_model="Unknown",
                is_open_source=None,
                tech_stack=[],
                description="Failed",
                api_available=None,
                language_support=[],
                integration_capabilities=[],
            )

    def _research_step(self, state: ResearchState) -> dict[str, Any]:
        extracted_tools = getattr(state, "extracted_tools", [])

        if not extracted_tools:
            print("⚠️ No extracted tools found, falling back to direct search")
            search_results = self.firecrawl.search_companies(
                query=state.query, num_results=4
            )
            tool_names = [
                result.get("metadata", {}).get("title", "Unknown")
                for result in search_results.data
            ]
        else:
            tool_names = extracted_tools

        print(f"🔬 Researching specific tools: {', '.join(tool_names)}")

        companies = []
        for tool_name in tool_names:
            tool_search_results = self.firecrawl.search_companies(
                query=tool_name + " official site", num_results=1
            )

            if tool_search_results:
                result = tool_search_results.data[0]
                url = result.get("url", "")

                company = CompanyInfo(
                    name=tool_name,
                    description=result.get("markdown", ""),
                    website=url,
                    tech_stack=[],
                    competitors=[],
                )
                scraped = self.firecrawl.scrape_company_page(url=url)

                if scraped:
                    content = scraped.markdown
                    analysis = self._analyze_company_content(
                        company_name=company.name, content=content
                    )

                    company.pricing_model = analysis.pricing_model
                    company.is_open_source = analysis.is_open_source
                    company.tech_stack = analysis.tech_stack
                    company.description = analysis.description
                    company.api_available = analysis.api_available
                    company.language_support = analysis.language_support
                    company.integration_capabilities = analysis.integration_capabilities

                companies.append(company)

        return {"companies": companies}

    def _analyze_step(self, state: ResearchState) -> dict[str, Any]:
        print("Generating Recommendations")

        company_data = ", ".join(
            [company.model_dump_json() for company in state.companies]
        )

        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(
                content=self.prompts.recommendations_user(
                    query=state.query, company_data=company_data
                )
            ),
        ]

        response = self.llm.invoke(messages)
        return {"analysis": response.content}

    def run(self, query: str) -> ResearchState:
        print(settings.FIRECRAWL_API_KEY)
        initial_state = ResearchState(query=query)
        final_state = self.workflow.invoke(initial_state)

        return ResearchState(**final_state)
