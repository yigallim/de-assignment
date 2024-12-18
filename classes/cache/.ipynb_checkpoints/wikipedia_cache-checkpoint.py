import redis
import threading

class WikipediaCache:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host='localhost', port=6379, db=0):
        if not hasattr(self, "redis_client"):
            self.redis_client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
            self.hash_name = "wikipedia_articles_html"

    def set_article(self, title, html_content):
        self.redis_client.hset(self.hash_name, title, html_content)

    def get_article(self, title):
        return self.redis_client.hget(self.hash_name, title)

    def delete_article(self, title):
        self.redis_client.hdel(self.hash_name, title)

    def get_all_articles(self):
        return self.redis_client.hgetall(self.hash_name)

    def article_exists(self, title):
        return self.redis_client.hexists(self.hash_name, title)

    def clear_all_articles(self):
        self.redis_client.delete(self.hash_name)

    def get_count(self):
        return self.redis_client.hlen(self.hash_name)

    def __repr__(self):
        articles = self.get_all_articles()
        if not articles:
            return "WikipediaCache(No articles in cache.)"
        return "WikipediaCache(\n" + "\n".join(
            [f"  Title: {title}\n  Content:\n{content}\n{'-' * 40}" for title, content in articles.items()]
        ) + "\n)"
