from __future__ import annotations

import json
from typing import Any

from app.analysis import llm_client


GROUP_KEYS = ("representative_papers", "recent_important_papers", "interest_related_papers", "supporting_papers")


def classify_papers(payload: dict[str, Any], fallback_groups: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    try:
        data = llm_client.call_llm_json(_prompt(payload))
    except (llm_client.LLMUnavailable, llm_client.LLMCallError, ValueError):
        return {
            **fallback_groups,
            "warnings": [],
            "llm_used": False,
            "llm_provider": None,
        }

    allowed_ids = {
        str(paper.get("id"))
        for paper in payload.get("candidate_papers", [])
        if paper.get("match_status") != "rejected" and paper.get("id") is not None
    }
    result = {key: [dict(item) for item in fallback_groups.get(key, [])] for key in GROUP_KEYS}
    for key in GROUP_KEYS:
        updates = _updates_by_id(data.get(key), allowed_ids)
        for item in result[key]:
            update = updates.get(str(item.get("id")))
            if update:
                item["category_reason"] = update.get("category_reason") or item.get("category_reason")
                item["why_read_this"] = update.get("why_read_this") or item.get("why_read_this")
                item["reason"] = item.get("category_reason")
    return {
        **result,
        "warnings": _as_list(data.get("warnings")),
        "llm_used": True,
        "llm_provider": llm_client.provider_name(),
    }


def _prompt(payload: dict[str, Any]) -> str:
    safe_payload = {
        "professor_name": payload.get("professor_name"),
        "user_interest": payload.get("user_interest"),
        "overall_keywords": payload.get("overall_keywords") or [],
        "recent_keywords": payload.get("recent_keywords") or [],
        "candidate_papers": [
            {
                "id": paper.get("id"),
                "title": paper.get("title"),
                "year": paper.get("year"),
                "paper_summary": paper.get("paper_summary"),
                "abstract": paper.get("abstract"),
                "source_keywords": paper.get("source_keywords") or paper.get("keywords") or [],
                "source_list": paper.get("source_list") or [],
                "match_status": paper.get("match_status"),
                "author_role": paper.get("author_role"),
                "scores": paper.get("scores") or {},
            }
            for paper in payload.get("candidate_papers", [])
            if paper.get("match_status") != "rejected"
        ],
    }
    return f"""
Write concise category reasons for LabFit paper cards.
Candidate selection has already been done by deterministic scores. Do not add new papers.
Use only papers listed in candidate_papers. Do not recommend rejected papers.
Do not evaluate paper quality or professor quality.

Return JSON:
{{
  "representative_papers": [{{"paper_id": "id", "category_reason": "...", "why_read_this": "..."}}],
  "recent_important_papers": [{{"paper_id": "id", "category_reason": "...", "why_read_this": "..."}}],
  "interest_related_papers": [{{"paper_id": "id", "category_reason": "...", "why_read_this": "..."}}],
  "supporting_papers": [{{"paper_id": "id", "category_reason": "..."}}],
  "warnings": []
}}

Evidence JSON:
{json.dumps(safe_payload, ensure_ascii=False)}
""".strip()


def _updates_by_id(value: Any, allowed_ids: set[str]) -> dict[str, dict[str, str]]:
    if not isinstance(value, list):
        return {}
    updates: dict[str, dict[str, str]] = {}
    for item in value:
        if not isinstance(item, dict):
            continue
        paper_id = str(item.get("paper_id") or item.get("id") or "")
        if paper_id not in allowed_ids:
            continue
        updates[paper_id] = {
            "category_reason": str(item.get("category_reason") or "").strip(),
            "why_read_this": str(item.get("why_read_this") or "").strip(),
        }
    return updates


def _as_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]
