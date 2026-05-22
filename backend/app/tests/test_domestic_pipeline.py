from types import SimpleNamespace

from app.analysis.keyword_extractor import extract_keywords
from app.analysis.trend_analyzer import analyze_trends
from app.paper_sources.base import load_sample_json
from app.papers.matcher import NEEDS_REVIEW, WEAK_CANDIDATE, score_master_paper_match
from app.papers.normalizer import normalize_dbpia_item, normalize_kci_item, normalize_riss_item, normalize_scienceon_item
from app.services.paper_harvest_service import default_adapters


def test_openalex_is_not_in_default_adapters(monkeypatch) -> None:
    monkeypatch.delenv("LABFIT_USE_MOCK_ONLY", raising=False)
    names = [adapter.source_name for adapter in default_adapters()]

    assert "openalex" not in names
    assert {"kci", "riss", "dbpia", "scienceon", "crossref"}.issubset(set(names))


def test_domestic_sources_normalize_to_common_candidate_schema() -> None:
    kci = normalize_kci_item(load_sample_json("sample_kci_response.json")["papers"][0])
    riss = normalize_riss_item(load_sample_json("sample_riss_response.json")["papers"][0])
    dbpia = normalize_dbpia_item(load_sample_json("sample_dbpia_response.json")["papers"][0])
    scienceon = normalize_scienceon_item(load_sample_json("sample_scienceon_response.json")["papers"][0])

    assert {kci.source, riss.source, dbpia.source, scienceon.source} == {"kci", "riss", "dbpia", "scienceon"}
    assert all(candidate.normalized_title for candidate in [kci, riss, dbpia, scienceon])
    assert kci.title_ko and riss.title_ko and dbpia.title_ko and scienceon.title_ko


def test_missing_affiliation_name_match_is_preserved_for_review() -> None:
    professor = SimpleNamespace(
        name="김민준",
        english_name="Minjun Kim",
        university="샘플대학교",
        department="컴퓨터공학과",
        official_keywords="LLM, 자연어처리, 교육 AI",
    )
    paper = {
        "display_title": "LLM 기반 맞춤형 학습 피드백 서비스 연구",
        "authors": ["김민준"],
        "author_affiliations": [],
        "year": 2025,
        "venue": "교육AI연구",
        "abstract": "LLM과 자연어처리를 활용한 학습자 피드백",
        "keywords": ["LLM", "자연어처리", "교육 AI"],
        "source_list": ["riss"],
        "source_confidence_signals": {"riss": 0.65},
        "citation_signals": {"riss": None},
    }

    result = score_master_paper_match(professor, paper)

    assert result.status in {NEEDS_REVIEW, WEAK_CANDIDATE}
    assert result.status != "rejected"


def test_keyword_extractor_removes_menu_and_generic_words() -> None:
    keywords = extract_keywords(
        [
            "학과소개 교수진 연구 논문 대학교 자연어처리 생성형 AI 학습자 피드백 추천시스템",
            "large language model natural language processing recommendation system",
        ],
        top_k=8,
    )

    forbidden = {"논문", "연구", "대학교", "학과소개", "교수진"}
    assert forbidden.isdisjoint(set(keywords))
    assert any(
        any(term in keyword for term in ["자연어처리", "생성형", "AI", "학습자 피드백", "recommendation"])
        for keyword in keywords
    )


def test_trend_analyzer_separates_paper_categories() -> None:
    result = analyze_trends(
        [
            {
                "id": 1,
                "display_title": "LLM 기반 맞춤형 학습 피드백 서비스 연구",
                "abstract": "LLM 자연어처리 교육 AI 학습자 피드백",
                "keywords": ["LLM", "자연어처리", "교육 AI"],
                "year": 2025,
                "venue": "교육AI연구",
                "match_status": "accepted",
                "match_score": 0.86,
                "author_role": "first_author",
                "citation_signals": {"kci": 4, "scienceon": 5},
                "source_list": ["kci", "scienceon"],
            },
            {
                "id": 2,
                "display_title": "디지털 도서관 추천을 위한 협업 필터링 모델",
                "abstract": "추천시스템 협업 필터링 정보검색",
                "keywords": ["추천시스템", "협업 필터링"],
                "year": 2016,
                "venue": "정보시스템연구",
                "match_status": "accepted",
                "match_score": 0.78,
                "author_role": "last_author",
                "citation_signals": {"kci": 32},
                "source_list": ["kci", "riss"],
            },
            {
                "id": 3,
                "display_title": "학습 성찰 텍스트마이닝",
                "abstract": "텍스트마이닝 학습분석",
                "keywords": ["텍스트마이닝", "학습분석"],
                "year": 2023,
                "venue": "학습분석학회지",
                "match_status": "needs_review",
                "match_score": 0.56,
                "author_role": "first_author",
                "citation_signals": {"dbpia": 3},
                "source_list": ["dbpia"],
            },
        ],
        "LLM, 자연어처리, 추천시스템, 교육 AI",
    )

    assert result["trend_summary"]
    assert result["representative_papers"]
    assert result["recent_important_papers"]
    assert result["supporting_papers"]
