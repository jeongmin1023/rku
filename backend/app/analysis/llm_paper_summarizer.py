from __future__ import annotations

import json
import re
from typing import Any

from app.analysis import llm_client
from app.analysis.keyword_extractor import extract_keywords


def summarize_paper(paper: dict[str, Any]) -> dict[str, Any]:
    fallback = fallback_paper_summary(paper)
    prompt = _prompt(paper)
    try:
        data = llm_client.call_llm_json(prompt)
    except (llm_client.LLMUnavailable, llm_client.LLMCallError, ValueError):
        return fallback

    summary = _clean_text(data.get("paper_summary")) or fallback["paper_summary"]
    limitations = _as_list(data.get("limitations")) or fallback["summary_limitations"]
    if paper.get("match_status") == "needs_review" and "검증 필요 후보" not in limitations:
        limitations.append("검증 필요 후보")
    if not paper.get("abstract") and "초록 부족" not in limitations:
        limitations.append("초록 부족")

    return {
        "paper_summary": summary,
        "main_topic": _clean_text(data.get("main_topic")) or fallback["main_topic"],
        "method_or_focus": _clean_text(data.get("method_or_focus")) or fallback["method_or_focus"],
        "why_it_matters": _clean_text(data.get("why_it_matters")) or fallback["why_it_matters"],
        "summary_limitations": list(dict.fromkeys(limitations)),
        "llm_used": True,
        "llm_provider": llm_client.provider_name(),
    }


def fallback_paper_summary(paper: dict[str, Any]) -> dict[str, Any]:
    title = paper.get("display_title") or paper.get("title_ko") or paper.get("title_en") or paper.get("title") or "제목 미상 논문"
    abstract = paper.get("abstract") or ""
    keywords = [str(keyword) for keyword in paper.get("keywords") or [] if keyword]
    limitations = ["LLM 요약 미사용"]
    if paper.get("match_status") == "needs_review":
        limitations.append("검증 필요 후보")
    if not abstract:
        limitations.append("초록 부족")

    if abstract:
        sentences = _sentences(abstract)
        paper_summary = " ".join(sentences[:2]) or abstract[:220]
    else:
        keyword_text = ", ".join(keywords[:4]) if keywords else "공개 키워드 부족"
        paper_summary = (
            f"초록 데이터가 없어 제목과 키워드 기준으로만 확인됩니다. "
            f"이 논문은 '{title}' 주제를 다루는 공개 논문 후보이며, 확인 가능한 키워드는 {keyword_text}입니다."
        )

    topic = keywords[0] if keywords else _topic_from_title(title)
    return {
        "paper_summary": paper_summary,
        "main_topic": topic,
        "method_or_focus": _method_or_focus(abstract, title),
        "why_it_matters": "연구실 탐색 관점에서 이 논문은 공개된 연구 주제와 최근 관심 축을 확인하는 근거로 볼 수 있습니다.",
        "summary_limitations": list(dict.fromkeys(limitations)),
        "llm_used": False,
        "llm_provider": None,
    }


def _prompt(paper: dict[str, Any]) -> str:
    safe_payload = {
        "title": paper.get("display_title") or paper.get("title"),
        "abstract": paper.get("abstract"),
        "keywords": paper.get("keywords") or [],
        "year": paper.get("year"),
        "venue": paper.get("venue"),
        "source_list": paper.get("source_list") or [],
        "match_status": paper.get("match_status"),
        "author_role": paper.get("author_role"),
    }
    return f"""
You summarize a paper candidate for LabFit. LabFit is not a professor ranking or evaluation tool.
Use only the provided title, abstract, keywords, year, venue, source, match status, and author role.
Do not invent papers, citation counts, journal impact, methods, or keywords.
If the abstract is missing, clearly say the summary is based on title and keywords.
If match_status is needs_review, mention that this is based on a verification-needed candidate.
Avoid evaluation words such as excellent, top, recommended professor, strong professor, or paper quality.

Return JSON with:
{{
  "paper_summary": "2-3 Korean sentences",
  "main_topic": "core topic",
  "method_or_focus": "method/target/focus or null",
  "why_it_matters": "what this paper helps a student understand about the lab direction",
  "limitations": ["..."]
}}

Evidence JSON:
{json.dumps(safe_payload, ensure_ascii=False)}
""".strip()


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?。])\s+|(?<=[다요음임됨함])\.\s*", text.strip())
    return [part.strip() for part in parts if part.strip()]


def _topic_from_title(title: str) -> str:
    keywords = extract_keywords([title], top_k=1)
    return keywords[0] if keywords else title[:40]


def _method_or_focus(abstract: str, title: str) -> str | None:
    text = f"{title} {abstract}".lower()
    for keyword in ["survey", "experiment", "case study", "deep learning", "machine learning", "llm", "분석", "모형", "딥러닝"]:
        if keyword in text:
            return keyword
    return None


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]
