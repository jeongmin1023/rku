from __future__ import annotations

import re
from collections import Counter


KOREAN_STOPWORDS = {
    "연구",
    "논문",
    "분석",
    "방법",
    "결과",
    "학회",
    "학술지",
    "대학교",
    "대학",
    "학과",
    "교수",
    "교수진",
    "소개",
    "저자",
    "초록",
    "키워드",
    "발행",
    "게재",
    "한국",
    "국내",
    "국제",
    "시스템",
    "영향",
    "기반",
    "활용",
    "적용",
    "서비스",
    "모델",
    "데이터",
}

MENU_STOPWORDS = {
    "학과소개",
    "교수소개",
    "교수진",
    "학생활동",
    "입학안내",
    "공지사항",
    "교육과정",
    "학사안내",
    "커뮤니티",
    "자료실",
    "오시는길",
    "로그인",
    "홈페이지",
}

ENGLISH_STOPWORDS = {
    "and",
    "the",
    "for",
    "with",
    "from",
    "using",
    "based",
    "study",
    "analysis",
    "research",
    "journal",
    "university",
    "paper",
    "article",
    "conference",
    "professor",
    "department",
    "korea",
    "korean",
    "system",
    "systems",
    "method",
    "methods",
    "result",
    "results",
    "effect",
    "effects",
    "model",
    "models",
    "data",
    "service",
    "services",
    "approach",
}

STOPWORDS = KOREAN_STOPWORDS | MENU_STOPWORDS | ENGLISH_STOPWORDS


def extract_keywords(
    texts: list[str],
    concepts: list[str] | None = None,
    top_k: int = 8,
    exclude_terms: list[str] | None = None,
) -> list[str]:
    exclude = {_normalize(term) for term in exclude_terms or [] if term}
    counts: Counter[str] = Counter()
    for text in texts:
        cleaned = _clean_text(text)
        tokens = _tokens(cleaned, exclude)
        title_like_weight = 2 if len(cleaned) <= 180 else 1
        counts.update({token: title_like_weight for token in tokens})
        counts.update({phrase: title_like_weight + 1 for phrase in _phrases(tokens, exclude)})

    for concept in concepts or []:
        normalized = _normalize_keyword(concept)
        if _keep_keyword(normalized, exclude):
            counts[normalized] += 4

    return [keyword for keyword, _ in counts.most_common(top_k)]


def similarity(text_a: str, text_b: str) -> float:
    tokens_a = set(_tokens(_clean_text(text_a), set()))
    tokens_b = set(_tokens(_clean_text(text_b), set()))
    tokens_a.update(_phrases(list(tokens_a), set()))
    tokens_b.update(_phrases(list(tokens_b), set()))
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


def _tokens(text: str, exclude: set[str]) -> list[str]:
    raw_tokens = re.findall(r"[A-Za-z가-힣0-9+#.-]{2,}", text)
    tokens: list[str] = []
    for token in raw_tokens:
        normalized = _normalize_keyword(token)
        if _keep_keyword(normalized, exclude):
            tokens.append(normalized)
    return tokens


def _phrases(tokens: list[str], exclude: set[str]) -> list[str]:
    phrases: list[str] = []
    for size in (4, 3, 2):
        for index in range(0, max(0, len(tokens) - size + 1)):
            phrase_tokens = tokens[index : index + size]
            phrase = " ".join(phrase_tokens)
            if _keep_phrase(phrase, phrase_tokens, exclude):
                phrases.append(phrase)
    return phrases


def _keep_phrase(phrase: str, tokens: list[str], exclude: set[str]) -> bool:
    if any(token in STOPWORDS or token in exclude for token in tokens):
        return False
    if len(phrase) > 48:
        return False
    has_topic_signal = any(token.upper() in {"AI", "LLM"} or len(token) >= 3 for token in tokens)
    return has_topic_signal


def _keep_keyword(keyword: str, exclude: set[str]) -> bool:
    if not keyword or keyword in STOPWORDS or keyword in exclude:
        return False
    if len(keyword) <= 1:
        return False
    if keyword.isdigit() or re.fullmatch(r"(19|20)\d{2}", keyword):
        return False
    if re.search(r"https?://|@|www\.", keyword):
        return False
    if len(keyword) > 40:
        return False
    return True


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"https?://\S+|[\w.+-]+@[\w-]+(?:\.[\w-]+)+", " ", text or "")).strip()


def _normalize_keyword(value: str) -> str:
    value = value.strip(" .,;:()[]{}<>\"'")
    if not value:
        return ""
    if value.upper() in {"AI", "LLM", "NLP", "CT"}:
        return value.upper()
    return value.lower()


def _normalize(value: str) -> str:
    return re.sub(r"\s+", "", value.lower())
