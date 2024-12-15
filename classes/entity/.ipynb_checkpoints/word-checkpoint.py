import classes.entity.defition_example_entry import DefinitionExampleEntry

class Word:
    def __init__(
        self,
        word: str,
        definitions: List[DefinitionExampleEntry],
        part_of_speech: List[str],
        sentiment_score: float,
        sentiment_type: SentimentType,
        antonyms: List[str] = None,
        synonyms: List[str] = None,
    ):
        """
        Initialize a Word object.

        :param word: The word itself (string).
        :param definitions: A list of DefinitionExampleEntry objects.
        :param part_of_speech: A list of parts of speech (e.g., ["noun", "verb"]).
        :param sentiment_score: The sentiment score of the word (float).
        :param sentiment_type: The type of sentiment (SentimentType enum).
        :param antonyms: A list of antonyms (optional).
        :param synonyms: A list of synonyms (optional).
        """
        self.word = word
        self.definitions = definitions
        self.part_of_speech = part_of_speech
        self.sentiment_score = sentiment_score
        self.sentiment_type = sentiment_type
        self.antonyms = antonyms or []
        self.synonyms = synonyms or []

    def __repr__(self):
        return (
            f"Word(word={self.word!r}, definitions={self.definitions!r}, "
            f"part_of_speech={self.part_of_speech!r}, sentiment_score={self.sentiment_score!r}, "
            f"sentiment_type={self.sentiment_type!r}, antonyms={self.antonyms!r}, synonyms={self.synonyms!r})"
        )

    def add_definition(self, definition: DefinitionExampleEntry):
        self.definitions.append(definition)

    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "definitions": [definition.to_dict() for definition in self.definitions],
            "part_of_speech": self.part_of_speech,
            "sentiment_score": self.sentiment_score,
            "sentiment_type": self.sentiment_type.value,
            "antonyms": self.antonyms,
            "synonyms": self.synonyms,
        }

    @classmethod
    def from_dict(cls, data: dict):
        definitions = [
            DefinitionExampleEntry.from_dict(defn)
            for defn in data.get("definitions", [])
        ]
        sentiment_type = SentimentType(data.get("sentiment_type", "Neutral"))
        return cls(
            word=data.get("word", ""),
            definitions=definitions,
            part_of_speech=data.get("part_of_speech", []),
            sentiment_score=data.get("sentiment_score", 0.0),
            sentiment_type=sentiment_type,
            antonyms=data.get("antonyms", []),
            synonyms=data.get("synonyms", []),
        )