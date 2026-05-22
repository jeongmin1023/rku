from __future__ import annotations

import re
import time

import requests
from bs4 import BeautifulSoup

from app.crawler.department_crawler import USER_AGENT


PUBLICATION_HINTS = ("publication", "publications", "논문", "연구실적", "papers")


def extract_lab_publication_titles(url: str | None, timeout: int = 10) -> list[str]:
    """Best-effort lab/profile publication title extraction.

    This is intentionally conservative. Results are only used as supporting
    evidence, never as the sole reason to accept a paper.
    """

    if not url:
        return []
    try:
        time.sleep(0.3)
        response = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    for noisy in soup(["script", "style", "noscript"]):
        noisy.decompose()

    candidates: list[str] = []
    for node in soup.find_all(["li", "p", "div", "article"]):
        text = re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()
        if len(text) < 20 or len(text) > 260:
            continue
        lowered = text.lower()
        if any(hint in lowered for hint in PUBLICATION_HINTS) or _looks_like_paper_title(text):
            candidates.append(_strip_year_prefix(text))
    return list(dict.fromkeys(candidates))[:80]


def _looks_like_paper_title(text: str) -> bool:
    has_year = bool(re.search(r"\b(19|20)\d{2}\b", text))
    has_title_shape = sum(ch.isalpha() for ch in text) >= 12
    return has_year and has_title_shape


def _strip_year_prefix(text: str) -> str:
    return re.sub(r"^\s*(?:\[?\d{4}\]?\.?\s*)", "", text).strip()
