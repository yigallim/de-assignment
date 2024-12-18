class DefinitionExampleEntry:
    def __init__(self, meaning: str, examples: list[str]):
        self.meaning = meaning
        self.examples = examples

    def __repr__(self):
        examples_repr = "\n  ".join(self.examples) if self.examples else "None"
        return f"DefinitionExampleEntry(\n  meaning={self.meaning!r},\n  examples=[\n  {examples_repr}\n  ]\n)"

    def add_example(self, example: str):
        self.examples.append(example)

    def to_dict(self) -> dict:
        return {"meaning": self.meaning, "examples": self.examples}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(meaning=data.get("meaning", ""), examples=data.get("examples", []))
