from firecrawl import FirecrawlApp, ScrapeOptions

from src.config.settings import settings


class FirecrawlService:
    def __init__(self):
        self.app = FirecrawlApp(api_key=settings.FIRECRAWL_API_KEY)

    def search_companies(self, query: str, num_results: int = 5) -> list:
        try:
            result = self.app.search(
                query=f"{query} company pricing",
                limit=num_results,
                scrape_options=ScrapeOptions(formats=["markdown"]),
            )
            return result
        except Exception as e:
            print(e)
            return []

    def scrape_company_page(self, url: str):
        try:
            result = self.app.scrape_url(url=url, formats=["markdown"])
            return result
        except Exception as e:
            print(e)
            return None
