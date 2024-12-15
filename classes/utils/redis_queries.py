import redis


class RedisQueries:
    def __init__(self, host="localhost", port=6379, decode_responses=True):
        self.redis_client = redis.StrictRedis(host=host, port=port, decode_responses=decode_responses)

    def show_memory_usage(self):
        memory_info = self.redis_client.info("memory")
        used_memory = memory_info.get("used_memory", None)

        if used_memory is not None:
            used_memory_mb = used_memory / (1024 * 1024)
            print(f"Redis is currently using approximately {used_memory_mb:.2f} MB of memory.")
        else:
            print("Could not retrieve memory usage.")
            
    def show_all_keys(self):
        keys = self.redis_client.keys("*")  # '*' matches all keys
        if keys:
            print("Existing keys in Redis:")
            for key in keys:
                print(key)
        else:
            print("No keys found in Redis.")

    def delete_database(self):
        confirmation = (
            input("Are you sure you want to delete the entire Redis database? (yes/no): ")
            .strip()
            .lower()
        )
        if confirmation == "yes":
            self.redis_client.flushdb()
            print("Database deleted.")
        else:
            print("Operation canceled.")

    def show_word_count_top_50(self):
        hash_name = "word_count"
        if self.redis_client.exists(hash_name):
            total_words = self.redis_client.hlen(hash_name)
            print(f"Total words count: {total_words}")
    
            word_count = self.redis_client.hgetall(hash_name)
            sorted_word_count = sorted(word_count.items(), key=lambda x: int(x[1]), reverse=True)
            
            print(f"Top 50 entries from the '{hash_name}' hash:")
            for i, (word, count) in enumerate(sorted_word_count[:50], start=1):
                print(f"{i}. {word}: {count}")
        else:
            print(f"The hash '{hash_name}' does not exist in Redis.")

    def show_word_count_least_50(self, limit=50):
        hash_name = "word_count"
        if self.redis_client.exists(hash_name):
            total_words = self.redis_client.hlen(hash_name)
            print(f"Total words count: {total_words}")
    
            word_count = self.redis_client.hgetall(hash_name)
            sorted_word_count = sorted(word_count.items(), key=lambda x: int(x[1]))
    
            print(f"Least {limit} entries from the '{hash_name}' hash:")
            for i, (word, count) in enumerate(sorted_word_count[:limit], start=1):
                print(f"{i}. {word}: {count}")
        else:
            print(f"The hash '{hash_name}' does not exist in Redis.")
        
    def show_wikipedia_articles(self):
        hash_name = "wikipedia_articles_html"
        if self.redis_client.exists(hash_name):
            total_articles = self.redis_client.hlen(hash_name)
            print(f"'{hash_name}' contains {total_articles} articles.")
    
            articles = self.redis_client.hgetall(hash_name)
            print(f"First 10 articles from the '{hash_name}' hash (content truncated to 200 characters):")
            for i, (title, content) in enumerate(articles.items(), start=1):
                print(f"{i}. Title: {title}\n   Content: {content[:200]}...\n")
                if i == 10:
                    break
        else:
            print(f"The hash '{hash_name}' does not exist in Redis.")

    def show_prpm_words(self):
        hash_name = "prpm_words_html"
        if self.redis_client.exists(hash_name):
            total_words = self.redis_client.hlen(hash_name)  # Get the total number of entries in the hash
            words = self.redis_client.hgetall(hash_name)
            print(f"'{hash_name}' contains {total_words} words.")
            print(f"First 30 words from the '{hash_name}' hash (content truncated to 200 characters):")
            for i, (word, content) in enumerate(words.items(), start=1):
                print(f"{i}. Word: {word}\n   Content: {content[:200]}...\n")
                if i == 30:  # Limit to the first 30 words
                    break
        else:
            print(f"The hash '{hash_name}' does not exist in Redis.")
            
    def show_not_found_words(self, hash_name="prpm_words_html", limit=50):
        if not self.redis_client.exists(hash_name):
            print(f"The hash '{hash_name}' does not exist in Redis.")
            return

        print(f"Scanning for words with no content in the '{hash_name}' hash...")
        cursor = 0
        total_not_found = 0
        not_found_words = []

        while True:
            cursor, data = self.redis_client.hscan(hash_name, cursor=cursor, count=1000)
            for word, content in data.items():
                if not content:
                    total_not_found += 1
                    if len(not_found_words) < limit:
                        not_found_words.append(word)
            if cursor == 0:
                break

        print(f"Total words not found: {total_not_found}")

        if total_not_found > 0:
            display_limit = min(total_not_found, limit)
            print(f"Displaying up to {display_limit} not found words:")
            for i, word in enumerate(not_found_words, start=1):
                print(f"{i}. {word}")
            if total_not_found > limit:
                print(f"...and {total_not_found - limit} more not found words.")
        else:
            print("No words were marked as not found.")

    def show_found_words(self, hash_name="prpm_words_html", limit=50):
        if not self.redis_client.exists(hash_name):
            print(f"The hash '{hash_name}' does not exist in Redis.")
            return

        print(f"Scanning for words with content in the '{hash_name}' hash...")
        cursor = 0
        total_found = 0
        found_words = []

        while True:
            cursor, data = self.redis_client.hscan(hash_name, cursor=cursor, count=1000)
            for word, content in data.items():
                if content:
                    total_found += 1
                    if len(found_words) < limit:
                        found_words.append(word)
            if cursor == 0:
                break

        print(f"Total words found: {total_found}")

        if total_found > 0:
            display_limit = min(total_found, limit)
            print(f"Displaying up to {display_limit} found words:")
            for i, word in enumerate(found_words, start=1):
                print(f"{i}. {word}")
            if total_found > limit:
                print(f"...and {total_found - limit} more found words.")
        else:
            print("No words were marked as found.")