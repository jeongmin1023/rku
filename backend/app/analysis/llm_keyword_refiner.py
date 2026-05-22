from __future__ import annotations

import json
from typing import Any

from app.analysis import llm_client
from app.analysis.keyword_extractor import extract_keywords


def refine_keywords(payload: dict[str, Any], fallback: dict[str, list[str]]) -> dict[str, Any]:
    try:
        data = llm_client.call_llm_json(_prompt(payload))
    except (llm_client.LLMUnavailable, llm_client.LLMCallError, ValueError):
        return {
            **fallback,
            "keyword_groups": [],
            "warnings": [],
            "llm_used": False,
            "llm_provider": None,
        }

    evidence_terms = _evidence_terms(payload)
    refined = {
        "overall_keywords": _filter_keywords(data.get("overall_keywords"), evidence_terms) or fallback.get("overall_keywords", []),
        "recent_keywords": _filter_keywords(data.get("recent_keywords"), evidence_terms) or fallback.get("recent_keywords", []),
        "five_year_keywords": _filter_keywords(data.get("five_year_keywords"), evidence_terms) or fallback.get("five_year_keywords", []),
        "keyword_groups": _filter_groups(data.get("keyword_groups"), evidence_terms),
        "warnings": _as_list(data.get("warnings")),
        "llm_used": True,
        "llm_provider": llm_client.provider_name(),
    }
    return refined


def _prompt(payload: dict[str, Any]) -> str:
    safe_payload = {
        "professor_name": payload.get("professor_name"),
        "official_keywords": payload.get("official_keywords") or [],
        "raw_keywords": payload.get("raw_keywords") or [],
        "papers": [
            {
                "title": paper.get("display_title") or paper.get("title"),
                "abstract": paper.get("abstract"),
                "keywords": paper.get("keywords") or [],
                "year": paper.get("year"),
                "match_status": paper.get("match_status"),
            }
            for paper in payload.get("papers", [])[:12]
        ],
    }
    return f"""
Refine LabFit research keywords. LabFit is not a professor ranking or evaluation tool.
Use only the provided official keywords, raw keywords, and paper evidence.
Remove menu words and generic words. Merge Korean/English synonyms only when evidence supports them.
Do not create keywords that are not supported by the provided evidence.

Return JSON:
{{
  "overall_keywords": ["5-8 research topic keywords"],
  "recent_keywords": ["up to 5 recent keywords"],
  "five_year_keywords": ["up to 5 five-year keywords"],
  "keyword_groups": [
    {{"label": "topic", "related_terms": ["..."], "evidence_paper_titles": ["..."]}}
  ],
  "warnings": []
}}

Evidence JSON:
{json.dumps(safe_payload, ensure_ascii=False)}
""".strip()


def _evidence_terms(payload: dict[str, Any]) -> set[str]:
    texts = []
    texts.extend(payload.get("official_keywords") or [])
    texts.extend(payload.get("raw_keywords") or [])
    for paper in payload.get("papers", []):
        texts.append(paper.get("display_title") or paper.get("title") or "")
        texts.append(paper.get("abstract") or "")
        texts.extend(paper.get("keywords") or [])
    terms = {term.lower() for term in extract_keywords(texts, top_k=80)}
    terms.update(str(term).lower() for term in payload.get("official_keywords") or [])
    terms.update(str(term).lower() for term in payload.get("raw_keywords") or [])
    return terms


def _filter_keywords(value: Any, evidence_terms: set[str]) -> list[str]:
    filtered: list[str] = []
    for keyword in _as_list(value):
        lowered = keyword.lower()
        if lowered in evidence_terms or any(lowered in term or term in lowered for term in evidence_terms):
            filtered.append(keyword)
    return list(dict.fromkeys(filtered))[:8]


def _filter_groups(value: Any, evidence_terms: set[str]) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    groups: list[dict[str, Any]] = []
    for group in value:
        if not isinstance(group, dict):
            continue
        label = str(group.get("label") or "").strip()
        if not label:
            continue
        related = _filter_keywords(group.get("related_terms"), evidence_terms)
        groups.append(
            {
                "label": label,
                "related_terms": related,
                "evidence_paper_titles": _as_list(group.get("evidence_paper_titles"))[:5],
            }
        )
    return groups[:8]


def _as_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]
