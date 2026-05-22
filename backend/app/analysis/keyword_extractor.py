from __future__ import annotations

import re
from collections import Counter


STOPWORDS = {
    "and",
    "the",
    "for",
    "with",
    "from",
    "using",
    "based",
    "study",
    "analysis",
    "model",
    "models",
    "data",
    "system",
    "systems",
    "research",
    "approach",
    "method",
    "results",
    "대한",
    "연구",
    "분석",
    "기반",
    "위한",
    "통한",
    "활용",
    "서비스",
}


def extract_keywords(texts: list[str], concepts: list[str] | None = None, top_k: int = 8) -> list[str]:
    counts: Counter[str] = Counter()
    for text in texts:
        counts.update(_tokens(text))
        counts.update(_phrases(text))
    for concept in concepts or []:
        normalized = concept.strip()
        if normalized:
            counts[normalized] += 3
    return [keyword for keyword, _ in counts.most_common(top_k)]


def similarity(text_a: str, text_b: str) -> float:
    tokens_a = set(_tokens(text_a) + _phrases(text_a))
    tokens_b = set(_tokens(text_b) + _phrases(text_b))
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


def _tokens(text: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z가-힣0-9]{2,}", text.lower())
    return [token for token in tokens if token not in STOPWORDS and not token.isdigit()]


def _phrases(text: str) -> list[str]:
    rough = re.findall(r"(?:[A-Z][A-Za-z0-9-]+|[가-힣A-Za-z0-9-]+)(?:\s+(?:AI|LLM|[가-힣A-Za-z0-9-]+)){1,2}", text)
    phrases = []
    for phrase in rough:
        lowered = phrase.lower().strip()
        if 4 <= len(lowered) <= 40 and not any(word in STOPWORDS for word in lowered.split()):
            phrases.append(phrase.strip())
    return phrases
