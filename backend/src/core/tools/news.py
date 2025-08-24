from newsapi import NewsApiClient

from src.config.settings import settings


class NewsService:
    def __init__(self):
        self.news = NewsApiClient(api_key=settings.NEWS_API_KEY)

    def fetch_news(self, query: str, max_results: int = 5):
        """Fetches up to max_results news headlines with descriptions limited to 500 words."""
        everything = self.news.get_everything(
            q=query,
            page=1,
            sources="bbc-news,the-verge",
            domains="bbc.co.uk,techcrunch.com",
            language="en",
            sort_by="relevancy",
        )
        news = []
        for article in everything.get("articles", [])[:max_results]:
            description = article.get("description") or ""
            # Limit description to 500 words
            words = description.split()
            if len(words) > 100:
                description = " ".join(words[:100])
            news.append(
                {
                    "source": article.get("source"),
                    "author": article.get("author"),
                    "title": article.get("title"),
                    "description": description,
                }
            )
        return news
