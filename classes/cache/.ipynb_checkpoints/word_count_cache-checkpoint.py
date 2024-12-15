import redis
import threading

class WordCountCache:
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
            self.hash_name = "word_count"

    def set_word_count(self, word, count):
        self.redis_client.hset(self.hash_name, word, count)

    def get_word_count(self, word):
        count = self.redis_client.hget(self.hash_name, word)
        return int(count) if count else 0

    def delete_word(self, word):
        self.redis_client.hdel(self.hash_name, word)

    def get_all_word_counts(self):
        word_counts = self.redis_client.hgetall(self.hash_name)
        return {word: int(count) for word, count in word_counts.items()}

    def word_exists(self, word):
        return self.redis_client.hexists(self.hash_name, word)

    def clear_all_words(self):
        self.redis_client.delete(self.hash_name)

    def get_total_words(self):
        return self.redis_client.hlen(self.hash_name)

    def get_all_fields(self):
        return self.redis_client.hgetall(self.hash_name)
    
    def __repr__(self):
        all_fields = self.get_all_fields()
        if not all_fields:
            return "WordCountCache(No data in cache.)"
        
        sorted_fields = sorted(all_fields.items(), key=lambda x: (int(x[1]) if x[1].isdigit() else 0), reverse=True)
        return "WordCountCache(\n" + "\n".join([f"  {field}: {value}" for field, value in sorted_fields]) + "\n)"
