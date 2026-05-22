from pathlib import Path

from app.crawler.department_crawler import parse_professors


def test_sample_department_extracts_professors() -> None:
    html = (Path(__file__).resolve().parents[2] / "sample_data" / "sample_department.html").read_text(encoding="utf-8")
    professors = parse_professors(html, "샘플대학교", "컴퓨터공학과", "https://example.edu/faculty")

    assert len(professors) == 3
    assert professors[0].name == "김민준"
    assert professors[0].email == "minjun.kim@example.edu"
    assert "LLM" in (professors[0].official_keywords or "")
