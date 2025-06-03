import re

pattern = re.compile(r"- (.*?) - \*{0,2}(.*?)\*{0,2}$")


def get_glossary() -> list[tuple[str, str]]:
    glossary: list[tuple[str, str]] = []
    with open("glossary.md", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            match = pattern.match(line)
            if match:
                en_term, ru_term = match.groups()
                glossary.append((en_term, ru_term))
    return glossary
