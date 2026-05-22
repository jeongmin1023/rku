from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.schemas import ProfessorCandidate


USER_AGENT = "LabFitResearchMVP/0.1 (+https://example.local; respectful academic crawler)"
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
KOREAN_NAME_RE = re.compile(r"^[가-힣]{2,5}$")
ENGLISH_NAME_RE = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b")
ENGLISH_NAME_TOKEN_RE = re.compile(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}$")
TITLE_WORDS = ("교수", "부교수", "조교수", "전임", "Professor", "Lecturer", "Assistant Professor")
KEYWORD_LABELS = ("연구분야", "연구 분야", "Research", "전공", "관심분야", "키워드")
LAB_LABELS = ("연구실", "Lab", "Laboratory")


@dataclass
class CrawlResult:
    professors: list[ProfessorCandidate]
    warnings: list[str]


def fetch_html(url: str, timeout: int = 12) -> tuple[str, list[str]]:
    warnings: list[str] = []
    try:
        time.sleep(0.4)
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
        )
        response.raise_for_status()
        response.encoding = response.apparent_encoding or response.encoding
        return response.text, warnings
    except requests.RequestException as exc:
        warnings.append(f"URL을 가져오지 못해 샘플 HTML로 대체했습니다: {exc}")
        sample_path = Path(__file__).resolve().parents[2] / "sample_data" / "sample_department.html"
        return sample_path.read_text(encoding="utf-8"), warnings


def crawl_department_page(university: str, department: str, url: str) -> CrawlResult:
    html, warnings = fetch_html(url)
    professors = parse_professors(html, university, department, url)
    if not professors:
        warnings.append("교수 정보를 안정적으로 찾지 못해 샘플 후보를 사용했습니다.")
        professors = sample_professors(university, department, url)
    return CrawlResult(professors=professors, warnings=warnings)


def parse_professors(html: str, university: str, department: str, source_url: str) -> list[ProfessorCandidate]:
    soup = BeautifulSoup(html, "html.parser")
    for noisy in soup(["script", "style", "noscript", "nav", "header", "footer", "aside"]):
        noisy.decompose()

    candidates: list[ProfessorCandidate] = []
    seen: set[tuple[str, str | None]] = set()
    for block in _candidate_blocks(soup):
        text = _clean_text(block.get_text(" ", strip=True))
        if len(text) < 4:
            continue
        email = _extract_email(text)
        name = _extract_name(text)
        if not name and email:
            name = _nearest_name(block, email)
        if not name:
            continue

        profile_url = _first_link(block, source_url)
        english_name = _extract_english_name(text, name)
        title = _extract_title(text)
        lab_name = _extract_label_value(text, LAB_LABELS)
        keywords = _extract_label_value(text, KEYWORD_LABELS)
        lab_url = _lab_link(block, source_url)
        evidence = _evidence(text, email, keywords, profile_url)
        confidence = _confidence(email, keywords, profile_url, title, text)
        key = (name, email)
        if key in seen:
            continue
        seen.add(key)
        candidates.append(
            ProfessorCandidate(
                name=name,
                english_name=english_name,
                title=title,
                university=university,
                department=department,
                lab_name=lab_name,
                email=email,
                profile_url=profile_url,
                lab_url=lab_url,
                official_keywords=keywords,
                source_url=source_url,
                extraction_confidence=confidence,
                evidence=evidence,
            )
        )
    return candidates[:80]


def _candidate_blocks(soup: BeautifulSoup) -> list:
    selectors = [".professor", ".faculty", ".member", ".people", ".profile", "li", "tr", "article", "section", "div"]
    blocks = []
    for selector in selectors:
        for block in soup.select(selector):
            text = block.get_text(" ", strip=True)
            has_person_signal = EMAIL_RE.search(text) or any(word in text for word in TITLE_WORDS)
            if has_person_signal and 5 <= len(text) <= 1200:
                blocks.append(block)
    return blocks


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extract_email(text: str) -> str | None:
    match = EMAIL_RE.search(text)
    return match.group(0) if match else None


def _extract_name(text: str) -> str | None:
    tokens = re.split(r"[\s|,/·:()]+", text)
    for token in tokens[:20]:
        token = token.strip()
        if KOREAN_NAME_RE.match(token) and not token.endswith("교수"):
            return token
    english_match = ENGLISH_NAME_RE.search(text)
    return english_match.group(0) if english_match else None


def _nearest_name(block, email: str) -> str | None:
    text = _clean_text(block.get_text(" ", strip=True))
    before_email = text.split(email)[0]
    return _extract_name(before_email)


def _extract_english_name(text: str, korean_name: str) -> str | None:
    matches = ENGLISH_NAME_RE.findall(text)
    for match in matches:
        if match != korean_name and "Professor" not in match:
            return match
    return None


def _extract_title(text: str) -> str | None:
    if "부교수" in text:
        return "부교수"
    if "조교수" in text or "Assistant Professor" in text:
        return "조교수"
    if "교수" in text or "Professor" in text:
        return "교수"
    if "Lecturer" in text:
        return "Lecturer"
    return None


def _extract_label_value(text: str, labels: tuple[str, ...]) -> str | None:
    for label in labels:
        pattern = rf"{re.escape(label)}\s*[:：]?\s*(.+?)(?:\s+(?:Email|E-mail|메일|전화|Tel|Office|홈페이지|상세|$))"
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            value = match.group(1).strip(" -|")
            return value[:240] if value else None
    return None


def _first_link(block, source_url: str) -> str | None:
    for anchor in block.find_all("a", href=True):
        href = anchor["href"].strip()
        if href and not href.startswith("mailto:"):
            return urljoin(source_url, href)
    return None


def _lab_link(block, source_url: str) -> str | None:
    for anchor in block.find_all("a", href=True):
        label = anchor.get_text(" ", strip=True)
        href = anchor["href"].strip()
        if href.startswith("mailto:"):
            continue
        if any(word.lower() in (label + href).lower() for word in ("lab", "연구실", "laboratory")):
            return urljoin(source_url, href)
    return None


def _evidence(text: str, email: str | None, keywords: str | None, profile_url: str | None) -> list[str]:
    evidence = []
    if email:
        evidence.append("이메일 주변 블록에서 추출")
    if keywords:
        evidence.append("연구분야/Research 라벨 주변 텍스트 감지")
    if profile_url:
        evidence.append("상세 페이지 링크 감지")
    if any(word in text for word in TITLE_WORDS):
        evidence.append("교수 직함 텍스트 감지")
    return evidence or ["이름 패턴 기반 후보"]


def _confidence(
    email: str | None,
    keywords: str | None,
    profile_url: str | None,
    title: str | None,
    text: str,
) -> float:
    confidence = 0.35
    if email:
        confidence += 0.2
    if keywords:
        confidence += 0.15
    if profile_url:
        confidence += 0.1
    if title:
        confidence += 0.1
    if len(text) > 500:
        confidence -= 0.1
    return round(max(0.1, min(0.9, confidence)), 2)


def sample_professors(university: str, department: str, source_url: str) -> list[ProfessorCandidate]:
    return [
        ProfessorCandidate(
            name="김민준",
            english_name="Minjun Kim",
            title="교수",
            university=university,
            department=department,
            lab_name="Human-Centered AI Lab",
            email="minjun.kim@example.edu",
            profile_url=source_url,
            official_keywords="LLM, 자연어처리, 추천시스템, 교육 AI",
            source_url=source_url,
            extraction_confidence=0.75,
            evidence=["샘플 데이터", "연구 키워드 포함"],
        ),
        ProfessorCandidate(
            name="이서연",
            english_name="Seoyeon Lee",
            title="부교수",
            university=university,
            department=department,
            lab_name="Medical Vision Lab",
            email="sylee@example.edu",
            profile_url=source_url,
            official_keywords="의료 영상, 딥러닝, 임상 의사결정 지원",
            source_url=source_url,
            extraction_confidence=0.75,
            evidence=["샘플 데이터", "연구 키워드 포함"],
        ),
        ProfessorCandidate(
            name="박지훈",
            english_name="Jihoon Park",
            title="조교수",
            university=university,
            department=department,
            lab_name="Safety Systems Lab",
            email="jhpark@example.edu",
            profile_url=source_url,
            official_keywords="환자안전, 감염관리, 보건정보",
            source_url=source_url,
            extraction_confidence=0.72,
            evidence=["샘플 데이터", "신임 연구실 예시"],
        ),
    ]
