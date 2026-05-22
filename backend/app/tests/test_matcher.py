from types import SimpleNamespace

from app.papers.matcher import ACCEPTED, NEEDS_REVIEW, REJECTED, score_master_paper_match


def test_different_affiliation_same_name_is_not_accepted() -> None:
    professor = SimpleNamespace(
        name="이서연",
        english_name="Seoyeon Lee",
        university="샘플대학교",
        department="의공학과",
        official_keywords="의료 영상, 딥러닝, 임상 의사결정 지원",
    )
    paper = {
        "display_title": "Plasma Simulation for Semiconductor Process Optimization",
        "authors": ["Seoyeon Lee", "Michael Brown"],
        "author_affiliations": ["Other University Department of Electrical Engineering"],
        "year": 2022,
        "venue": "Semiconductor Engineering Letters",
        "doi": "10.5555/other.2022.404",
        "uci": "G704-OTHER.2022.404",
        "abstract": "Plasma simulation for semiconductor process optimization.",
        "keywords": ["Semiconductor", "Plasma"],
        "source_list": ["kci", "openalex"],
        "source_ids": {"kci": ["KCI-CONTAMINATION-001"], "openalex": ["https://openalex.org/WLEE2022404"]},
        "citation_signals": {"kci": 19, "openalex": 44},
        "duplicate_status": "merged",
    }

    result = score_master_paper_match(professor, paper)

    assert result.status in {REJECTED, NEEDS_REVIEW}
    assert result.score < 0.8


def test_middle_coauthor_low_topic_is_not_accepted() -> None:
    professor = SimpleNamespace(
        name="김민준",
        english_name="Minjun Kim",
        university="샘플대학교",
        department="컴퓨터공학과",
        official_keywords="LLM, 자연어처리, 추천시스템, 교육 AI",
    )
    paper = {
        "display_title": "A Genomics Workflow for Protein Folding Experiments",
        "authors": ["Ari Choi", "Minjun Kim", "Dana Lee"],
        "author_affiliations": ["샘플대학교 컴퓨터공학과"],
        "year": 2025,
        "venue": "Bioinformatics Practice",
        "doi": "10.5555/coauthor.2025.001",
        "uci": None,
        "abstract": "Protein folding genomics workflow.",
        "keywords": ["Genomics", "Protein folding"],
        "source_list": ["openalex", "crossref"],
        "source_ids": {"openalex": ["WCOAUTHOR"], "crossref": ["10.5555/coauthor.2025.001"]},
        "source_confidence_signals": {"openalex": 0.8, "crossref": 0.8},
        "citation_signals": {"openalex": 8, "crossref": 0},
        "duplicate_status": "merged",
        "merge_confidence": 0.95,
        "merge_notes": [],
    }

    result = score_master_paper_match(professor, paper)

    assert result.status != ACCEPTED
    assert "공동저자 오염 가능성" in result.warnings_json
