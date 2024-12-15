import redis
import threading

class PRPMCache:
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
            self.hash_name = "prpm_words_html"

    def set_word_page(self, word, html_content):
        self.redis_client.hset(self.hash_name, word, html_content)

    def get_word_page(self, word):
        return self.redis_client.hget(self.hash_name, word)

    def delete_word_page(self, word):
        self.redis_client.hdel(self.hash_name, word)

    def get_all_word_pages(self):
        return self.redis_client.hgetall(self.hash_name)

    def word_page_exists(self, word):
        return self.redis_client.hexists(self.hash_name, word)

    def clear_all_word_pages(self):
        self.redis_client.delete(self.hash_name)

    def get_word_count(self):
        return self.redis_client.hlen(self.hash_name)

    def __repr__(self):
        word_pages = self.get_all_word_pages()
        if not word_pages:
            return "PRPMCache(No word pages in cache.)"
        return "PRPMCache(\n" + "\n".join([f"  Word: {word}\n  Content:\n{content}\n{'-' * 40}" for word, content in word_pages.items()]) + "\n)"
