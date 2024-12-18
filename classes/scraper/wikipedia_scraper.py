import asyncio
import aiohttp
from bs4 import BeautifulSoup 

class WikipediaScraper:
    def __init__(self, max_concurrent_requests=10):
        self.session = None
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def fetch_article_titles(self, limit=500, search_term="history"):
        api_url="https://ms.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": search_term,
            "srlimit": limit,
            "format": "json"
        }
        try:
            async with self.semaphore:
                async with self.session.get(api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data['query']['search']
                        titles = {article['title'] for article in articles}
                        print(f"Fetched {len(titles)} article titles.")
                        return set(list(titles)[:limit])
                    else:
                        print("Error fetching data from Wikipedia API.")
                        return set()
        except Exception as e:
            print(f"Error fetching articles: {e}")
            return set()

    async def fetch_content(self, title):
        url = f"https://ms.wikipedia.org/wiki/{title.replace(' ', '_')}"
        async with self.semaphore:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    body_content = soup.find(id="bodyContent")
                    if body_content:
                        return body_content.decode_contents()
                    else:
                        print(f"bodyContent not found for title: {title}")
        return ""
