from app.analysis.trend_analyzer import analyze_trends


def test_few_accepted_papers_use_emerging_lab_mode() -> None:
    result = analyze_trends(
        [
            {
                "id": 1,
                "display_title": "Digital Surveillance Dashboard for Infection Control Practice",
                "abstract": "infection control and patient safety dashboard",
                "keywords": ["감염관리", "환자안전"],
                "year": 2025,
                "venue": "Patient Safety Informatics",
                "match_status": "accepted",
                "match_score": 0.86,
                "author_role": "first_author",
                "citation_signals": {"kci": 1, "openalex": 5},
            }
        ],
        "환자안전, 감염관리, 보건정보",
    )

    assert result["analysis_type"] == "emerging_lab"
    assert result["evidence_confidence"] == "low"
    assert "공개 논문 데이터" in result["trend_summary"]


def test_old_high_citation_paper_can_be_representative_but_recent_weight_is_low() -> None:
    result = analyze_trends(
        [
            {
                "id": 1,
                "display_title": "Classic Recommender Systems for Digital Libraries",
                "abstract": "collaborative filtering recommender systems",
                "keywords": ["추천시스템"],
                "year": 2014,
                "venue": "Information Systems",
                "match_status": "accepted",
                "match_score": 0.9,
                "author_role": "last_author",
                "citation_signals": {"kci": 50, "openalex": 180},
            },
            {
                "id": 2,
                "display_title": "LLM Feedback for Learning Analytics",
                "abstract": "LLM learning analytics education",
                "keywords": ["LLM", "교육 AI"],
                "year": 2025,
                "venue": "Educational AI",
                "match_status": "accepted",
                "match_score": 0.86,
                "author_role": "first_author",
                "citation_signals": {"openalex": 10},
            },
            {
                "id": 3,
                "display_title": "Text Mining Student Reflection",
                "abstract": "text mining transformer learning analytics",
                "keywords": ["텍스트마이닝"],
                "year": 2024,
                "venue": "Learning Analytics",
                "match_status": "accepted",
                "match_score": 0.82,
                "author_role": "first_author",
                "citation_signals": {"openalex": 8},
            },
        ],
        "LLM, 교육 AI, 추천시스템",
    )

    representative_titles = [paper["title"] for paper in result["representative_papers"]]
    recent_titles = [paper["title"] for paper in result["recent_papers"]]

    assert "Classic Recommender Systems for Digital Libraries" in representative_titles
    assert any(paper["label"] == "과거 대표 논문" for paper in result["representative_papers"])
    assert recent_titles[0] != "Classic Recommender Systems for Digital Libraries"
