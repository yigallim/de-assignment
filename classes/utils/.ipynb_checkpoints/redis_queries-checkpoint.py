import redis
from classes.cache.prpm_cache import PRPMCache
from classes.cache.dictionary_api_cache import DictionaryApiCache

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

    def show_word_count_top(self, count=50):
        hash_name = "word_count"
        if self.redis_client.exists(hash_name):
            total_words = self.redis_client.hlen(hash_name)
            print(f"Total words count: {total_words}")
    
            word_count = self.redis_client.hgetall(hash_name)
            sorted_word_count = sorted(word_count.items(), key=lambda x: int(x[1]), reverse=True)
            
            print(f"Top {count} entries from the '{hash_name}' hash:")
            for i, (word, count) in enumerate(sorted_word_count[:count], start=1):
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
                if i == 30:
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

    def show_wiktionary_not_found_words(self, limit=5):
        hash_name = "wiktionary_api_cache"
        if not self.redis_client.exists(hash_name):
            print(f"The hash '{hash_name}' does not exist in Redis.")
            return

        print(f"Scanning '{hash_name}' for words with no content...")
        cursor = 0
        total_not_found = 0
        not_found_words = []

        while True:
            cursor, data = self.redis_client.hscan(hash_name, cursor=cursor, count=1000)
            for word, content in data.items():
                if not content.strip():  # Check if content is empty
                    total_not_found += 1
                    if len(not_found_words) < limit:
                        not_found_words.append(word)

            if cursor == 0:
                break

        print(f"\nTotal words with no content: {total_not_found}")
        if not_found_words:
            print(f"First {len(not_found_words)} words with no content:")
            for i, word in enumerate(not_found_words, start=1):
                print(f"{i}. {word}")
            if total_not_found > limit:
                print(f"...and {total_not_found - limit} more words with no content.")
        else:
            print("No words without content found.")

    def show_wiktionary_found_words(self, limit=5):
        hash_name = "wiktionary_api_cache"
        if not self.redis_client.exists(hash_name):
            print(f"The hash '{hash_name}' does not exist in Redis.")
            return

        print(f"Scanning '{hash_name}' for words with content...")
        cursor = 0
        total_found = 0
        found_words = []

        while True:
            cursor, data = self.redis_client.hscan(hash_name, cursor=cursor, count=1000)
            for word, content in data.items():
                if content.strip():  # Check if content is non-empty
                    total_found += 1
                    if len(found_words) < limit:
                        found_words.append(word)

            if cursor == 0:
                break

        print(f"\nTotal words with content: {total_found}")
        if found_words:
            print(f"First {len(found_words)} words with content:")
            for i, word in enumerate(found_words, start=1):
                print(f"{i}. {word}")
            if total_found > limit:
                print(f"...and {total_found - limit} more words with content.")
        else:
            print("No words with content found.")
            
    def show_dictionary_api_words(self, limit=50):
        hash_name = "dictionary_api_cache"
        if not self.redis_client.exists(hash_name):
            print(f"The hash '{hash_name}' does not exist in Redis.")
            return

        print(f"Scanning the '{hash_name}' hash for words with and without definitions...")

        cursor = 0
        words_with_definitions = []
        words_without_definitions = []
        total_with_definitions = 0
        total_without_definitions = 0

        while True:
            cursor, data = self.redis_client.hscan(hash_name, cursor=cursor, count=1000)
            for word, content in data.items():
                if content.strip():
                    total_with_definitions += 1
                    if len(words_with_definitions) < limit:
                        words_with_definitions.append(word)
                else:
                    total_without_definitions += 1
                    if len(words_without_definitions) < limit:
                        words_without_definitions.append(word)

            if cursor == 0:
                break

        print(f"\nTotal words with definitions: {total_with_definitions}")
        print(f"Total words without definitions: {total_without_definitions}\n")

        if words_with_definitions:
            print(f"First {min(len(words_with_definitions), limit)} words with definitions:")
            for i, word in enumerate(words_with_definitions, start=1):
                print(f"{i}. {word}")

        if words_without_definitions:
            print(f"\nFirst {min(len(words_without_definitions), limit)} words without definitions:")
            for i, word in enumerate(words_without_definitions, start=1):
                print(f"{i}. {word}")

    
    def show_gcp_sentiment_data(self, limit=50, lang="all"):
        hash_name = "gcp_sentiment_cache"
    
        if not self.redis_client.exists(hash_name):
            print(f"The hash '{hash_name}' does not exist in Redis.")
            return
    
        print(f"Scanning '{hash_name}' for sentiment data... (Filter: {lang})")
    
        def _is_malay(word):
            """Check if a word is Malay by verifying it in the PRPM cache."""
            prpm_cache = PRPMCache()
            return  prpm_cache.is_malay(word)
    
        def _is_english(word):
            """Check if a word is English by verifying it in the Dictionary API cache."""
            dictionary_api_cache = DictionaryApiCache()
            return dictionary_api_cache.is_english(word)

        cursor = 0
        total_entries = 0
        sentiment_data = []
    
        while True:
            cursor, data = self.redis_client.hscan(hash_name, cursor=cursor, count=1000)
            for word, value in data.items():
                try:
                    if lang == "ms" and not _is_malay(word):
                        continue
                    elif lang == "en" and not _is_english(word):
                        continue
    
                    magnitude, score = map(float, value.split(","))
                    sentiment_data.append((word, magnitude, score))
                    total_entries += 1
                    if len(sentiment_data) >= limit:
                        break
                except ValueError:
                    continue
            if cursor == 0 or len(sentiment_data) >= limit:
                break
    
        # Output results
        print(f"\nTotal entries found in '{hash_name}' matching filter '{lang}': {total_entries}")
        print(f"Displaying up to {min(len(sentiment_data), limit)} entries:\n")
    
        for i, (word, magnitude, score) in enumerate(sentiment_data, start=1):
            print(f"{i}. Word: {word}, Sentiment Magnitude: {magnitude}, Sentiment Score: {score}")
    
        if total_entries > limit:
            print(f"...and {total_entries - limit} more entries not shown.")
