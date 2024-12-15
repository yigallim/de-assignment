import nest_asyncio
import asyncio
from asyncio import Semaphore
from classes.scraper.prpm_scraper import PRPMScraper
from classes.cache.prpm_cache import PRPMCache
from classes.utils.progress_tracker import ProgressTracker

class PRPMPipeline:
    def __init__(self, words=None, use_cache=True, batch_size=50, concurrency_limit=10):
        if words is None:
            words = []
        self.words = words
        self.use_cache = use_cache
        self.batch_size = batch_size
        self.concurrency_limit = concurrency_limit
        self.cache = PRPMCache()

    async def scrape_and_store(self):
        existing_cache = self.cache.get_all_word_pages() if self.use_cache else {}
        words_to_scrape = [w for w in self.words if w not in existing_cache] if self.use_cache else self.words
    
        print(f"Total words: {len(self.words)}")
        print(f"Cached words (skipped): {len(self.words) - len(words_to_scrape)}")
        print(f"Words to scrape: {len(words_to_scrape)}")
    
        semaphore = Semaphore(self.concurrency_limit)
    
        async with PRPMScraper() as scraper:
            tracker = ProgressTracker(len(words_to_scrape))
            scraped_count = 0
            found_count = 0
            not_found_count = 0
    
            async def process_word(word):
                nonlocal scraped_count, found_count, not_found_count
                async with semaphore:
                    content = await scraper.fetch_content(word)
                    self.cache.set_word_page(word, content if content else "")
                    scraped_count += 1
                    if content:
                        found_count += 1
                    else:
                        not_found_count += 1
                    tracker.update()
    
            for batch_start in range(0, len(words_to_scrape), self.batch_size):
                batch = words_to_scrape[batch_start:batch_start + self.batch_size]
                tasks = [process_word(word) for word in batch]
                await asyncio.gather(*tasks)
    
            tracker.complete()
            print("Summary:")
            print(f"Words scraped: {scraped_count}")
            print(f"Words found (with content): {found_count}")
            print(f"Words not found (no valid content): {not_found_count}")
            print()


    def run(self):
        nest_asyncio.apply()
        asyncio.run(self.scrape_and_store())
