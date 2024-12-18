import re
from bs4 import BeautifulSoup
from collections import Counter

class ArticleProcessor:
    @staticmethod
    def filter_nonsense(word_list):
        counts = Counter(word_list)
        return [w for w in word_list if len(w) >= 3 and counts[w] >= 5]
    
    @staticmethod
    def clean_text(text):
        return re.sub(r'[^a-zA-Z\s]', ' ', text).lower().strip()

    @staticmethod
    def get_words_from_meaningful_element_tag(html):
        if not html:
            return []

        if isinstance(html, str):
            html = BeautifulSoup(html, "html.parser")

        meaningful_tags = [
            'p',         # Paragraphs
            'li',        # List
            'caption',   # Table captions
            'dt', 'dd',  # Definition terms and descriptions
            'blockquote' # Blockquotes
        ]

        texts = []
        for tag in meaningful_tags:
            for element in html.find_all(tag):
                element_text = element.get_text()
                if element_text:
                    texts.append(element_text)
                    texts.append(' ')

        return ' '.join(texts)

