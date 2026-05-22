from app.analysis.fit_analyzer import analyze_fit


def test_fit_result_contains_level_and_interpretation() -> None:
    papers = [
        {
            "id": 1,
            "display_title": "Large Language Model Assisted Feedback for Personalized Learning Services",
            "abstract": "LLM educational services natural language processing feedback",
            "keywords": ["LLM", "교육 AI", "자연어처리"],
            "year": 2025,
            "venue": "Journal of Educational AI",
            "match_status": "accepted",
            "match_score": 0.88,
            "author_role": "first_author",
        },
        {
            "id": 2,
            "display_title": "Text Mining of Student Reflection Data Using Transformer Models",
            "abstract": "text mining transformer models learning analytics",
            "keywords": ["텍스트마이닝", "학습분석"],
            "year": 2023,
            "venue": "Learning Analytics Review",
            "match_status": "accepted",
            "match_score": 0.82,
            "author_role": "last_author",
        },
    ]

    result = analyze_fit("LLM 기반 교육 서비스", papers, "medium")

    assert result["fit_level"] in {"높음", "중간~높음", "중간", "낮음", "판단 보류"}
    assert result["interpretation"]
    assert result["check_points"]


def test_emerging_lab_fit_does_not_use_low_expression() -> None:
    papers = [
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
        }
    ]

    result = analyze_fit("감염관리와 환자안전", papers, "low")

    assert result["fit_level"] in {"판단 보류", "중간, 확인 필요"}
    assert "낮음" not in result["fit_level"]
