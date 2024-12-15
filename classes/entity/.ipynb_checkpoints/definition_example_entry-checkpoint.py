class DefinitionExampleEntry:
    def __init__(self, meaning: str, examples: list[str]):
        self.meaning = meaning
        self.examples = examples

    def __repr__(self):
        return f"DefinitionExampleEntry(meaning={self.meaning!r}, examples={self.examples!r})"

    def add_example(self, example: str):
        self.examples.append(example)

    def to_dict(self) -> dict:
        return {"meaning": self.meaning, "examples": self.examples}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(meaning=data.get("meaning", ""), examples=data.get("examples", []))
