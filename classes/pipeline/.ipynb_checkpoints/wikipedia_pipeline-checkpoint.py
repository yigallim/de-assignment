import asyncio
import nest_asyncio
import re
from collections import Counter
from pyspark.sql import SparkSession
from bs4 import BeautifulSoup
from classes.scraper.wikipedia_scraper import WikipediaScraper
from classes.cache.wikipedia_cache import WikipediaCache
from classes.cache.word_count_cache import WordCountCache
from classes.utils.progress_tracker import ProgressTracker
from classes.utils.article_processor import ArticleProcessor

class WikipediaPipeline:
    def __init__(self, search_term="history", limit=500, word_count_article_limit=1000, use_cache=True, batch_size=50):
        self.search_term = search_term
        self.limit = limit
        self.word_count_article_limit = word_count_article_limit
        self.use_cache = use_cache
        self.batch_size = batch_size
        self.wiki_cache = WikipediaCache()
        self.word_count_cache = WordCountCache()

    async def scrape_and_store(self):
        async with WikipediaScraper() as scraper:
            articles = await scraper.fetch_article_titles(limit=self.limit, search_term=self.search_term)
            print(f"Fetching {len(articles)} articles content.")
            
            tracker = ProgressTracker(len(articles))
            scraped_count = 0
            cached_count = 0
            tasks = []

            for title in articles:
                if self.use_cache and self.wiki_cache.article_exists(title):
                    cached_count += 1
                else:
                    tasks.append(self._scrape_and_cache_article(scraper, title))
                    scraped_count += 1

                if len(tasks) >= self.batch_size:
                    await asyncio.gather(*tasks)
                    tasks.clear()
                tracker.update()

            if tasks:
                await asyncio.gather(*tasks)
            tracker.complete()

            print(f"Summary:")
            print(f"Articles scraped from Wikipedia: {scraped_count}")
            print(f"Articles retrieved from cache: {cached_count}")
            print()

    async def _scrape_and_cache_article(self, scraper, title):
        content = await scraper.fetch_content(title)
        if content:
            self.wiki_cache.set_article(title, content)

    def store_word_counts(self):
        print(f"Storing tokenized words count using Spark and reduceByKey.")

        spark = SparkSession.builder \
            .appName("WikipediaWordCount") \
            .getOrCreate()

        articles = self.wiki_cache.get_all_articles()
        limited_articles = list(articles.items())[:self.word_count_article_limit]
        rdd = spark.sparkContext.parallelize(limited_articles)

        def tokenize_and_clean(article):
            title, content = article
            soup = BeautifulSoup(content, "html.parser")
            meaningful_tags = ['p', 'li', 'caption', 'dt', 'dd', 'blockquote']
            extracted_texts = []
            for tag in meaningful_tags:
                for element in soup.find_all(tag):
                    element_text = element.get_text()
                    if element_text:
                        extracted_texts.append(element_text+" ")
            combined_text = " ".join(extracted_texts)
            clean_content = re.sub(r'[^a-zA-Z\s]', ' ', combined_text).lower().strip()
            words = clean_content.split()
            return [(word, 1) for word in words]
        
        word_pairs_rdd = rdd.flatMap(tokenize_and_clean)
        word_counts_rdd = word_pairs_rdd.reduceByKey(lambda x, y: x + y)
        filtered_word_counts_rdd = word_counts_rdd.filter(lambda pair: len(pair[0]) >= 3 and pair[1] >= 15)
        word_count_dict = filtered_word_counts_rdd.collectAsMap()
        self.word_count_cache.clear_all_words()
        for word, count in word_count_dict.items():
            self.word_count_cache.set_word_count(word, count)
        
        print("Summary:")
        print(f"Total unique words stored: {len(word_count_dict)}")
        spark.stop()

    def run(self):
        nest_asyncio.apply()
        asyncio.run(self.scrape_and_store())
        self.store_word_counts()
