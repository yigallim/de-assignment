import asyncio
import aiohttp
from bs4 import BeautifulSoup 

class PRPMScraper:
    def __init__(self, max_concurrent_requests=10):
        self.session = None
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def fetch_content(self, word):
        url = f"https://prpm.dbp.gov.my/Cari1?keyword={word}"
        async with self.semaphore:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    main_content = soup.find(id="MainContent_panelresult")
                    if main_content and "<b>Kamus Bahasa Melayu</b>" in str(main_content):
                        return main_content.decode_contents()
        return ""
