import type {
  Analysis,
  ContactCard,
  CrawlResponse,
  FitResult,
  HarvestDepartmentResponse,
  ProfessorCard,
  ProfessorDetail,
  ProfessorPaper
} from "@/lib/types";

const department = {
  id: 1,
  university: "샘플대학교",
  department: "컴퓨터공학과",
  source_url: "https://example.edu/faculty",
  created_at: "2026-05-22T10:00:00Z"
};

const baseProfessors = [
  {
    id: 1,
    department_id: 1,
    name: "김민준",
    english_name: "Minjun Kim",
    title: "교수",
    university: "샘플대학교",
    department: "컴퓨터공학과",
    lab_name: "Human-Centered AI Lab",
    email: "minjun.kim@example.edu",
    profile_url: "https://example.edu/faculty/minjun-kim",
    lab_url: "https://example.edu/labs/hcai",
    official_keywords: "LLM, 자연어처리, 추천시스템, 교육 AI",
    source_url: "https://example.edu/faculty",
    extraction_confidence: 0.82,
    analysis_type: "domestic_db_based",
    evidence_confidence: "medium",
    created_at: "2026-05-22T10:00:00Z"
  },
  {
    id: 2,
    department_id: 1,
    name: "이서연",
    english_name: "Seoyeon Lee",
    title: "부교수",
    university: "샘플대학교",
    department: "컴퓨터공학과",
    lab_name: "Medical Vision Lab",
    email: "sylee@example.edu",
    profile_url: "https://example.edu/faculty/seoyeon-lee",
    lab_url: null,
    official_keywords: "의료 영상, 딥러닝, 임상 의사결정 지원",
    source_url: "https://example.edu/faculty",
    extraction_confidence: 0.78,
    analysis_type: "domestic_db_based",
    evidence_confidence: "medium",
    created_at: "2026-05-22T10:00:00Z"
  },
  {
    id: 3,
    department_id: 1,
    name: "박지훈",
    english_name: "Jihoon Park",
    title: "조교수",
    university: "샘플대학교",
    department: "컴퓨터공학과",
    lab_name: "Safety Systems Lab",
    email: "jhpark@example.edu",
    profile_url: "https://example.edu/faculty/jihoon-park",
    lab_url: null,
    official_keywords: "환자안전, 감염관리, 보건정보",
    source_url: "https://example.edu/faculty",
    extraction_confidence: 0.74,
    analysis_type: "emerging_lab",
    evidence_confidence: "low",
    created_at: "2026-05-22T10:00:00Z"
  }
] as const;

const kimPapers: ProfessorPaper[] = [
  paper(101, "LLM 기반 맞춤형 학습 피드백 서비스 연구", 2025, ["kci", "scienceon", "crossref"], { kci: 4, scienceon: 5, crossref: 0 }, "accepted", ["LLM", "자연어처리", "교육 AI"]),
  paper(102, "트랜스포머를 활용한 학습 성찰 텍스트 마이닝", 2023, ["kci", "dbpia"], { kci: 9, dbpia: 3 }, "needs_review", ["텍스트마이닝", "학습분석"]),
  paper(103, "디지털 도서관 추천을 위한 협업 필터링 모델", 2016, ["kci", "riss", "crossref"], { kci: 32, riss: null, crossref: 0 }, "needs_review", ["추천시스템", "협업 필터링"])
];

const leePapers: ProfessorPaper[] = [
  paper(201, "흉부 CT 결절 탐지를 위한 딥러닝 기반 의료 영상 분석", 2024, ["kci", "dbpia", "scienceon", "crossref"], { kci: 7, dbpia: 2, scienceon: 4, crossref: 0 }, "accepted", ["의료 영상", "딥러닝"]),
  paper(202, "반도체 공정 최적화를 위한 플라즈마 시뮬레이션", 2022, ["riss"], { riss: null }, "weak_candidate", ["반도체", "플라즈마"])
];

const parkPapers: ProfessorPaper[] = [
  paper(301, "감염관리 실무를 위한 디지털 감시 대시보드", 2025, ["scienceon", "dbpia", "crossref"], { scienceon: 1, dbpia: 0, crossref: 0 }, "needs_review", ["감염관리", "환자안전"])
];

function paper(
  id: number,
  title: string,
  year: number,
  sources: string[],
  citations: Record<string, number | null>,
  status: ProfessorPaper["match_status"],
  keywords: string[]
): ProfessorPaper {
  return {
    id,
    match_score: status === "accepted" ? 0.78 : status === "needs_review" ? 0.56 : 0.32,
    match_status: status,
    author_role: "first_author",
    warnings: status === "accepted" ? [] : ["검증 필요: 소속 또는 메타데이터 근거를 추가 확인하세요."],
    evidence_notes: {},
    master_paper: {
      id,
      title_ko: title,
      title_en: null,
      display_title: title,
      authors: ["김민준"],
      author_affiliations: ["샘플대학교"],
      year,
      venue: "샘플 학술지",
      doi: id === 102 ? null : `10.5555/labfit.${id}`,
      uci: `G704-SAMPLE.${id}`,
      abstract: `${keywords.join(", ")} 관련 공개 논문 후보입니다.`,
      keywords,
      source_list: sources,
      source_ids: Object.fromEntries(sources.map((source) => [source, [`${source}-${id}`]])),
      citation_signals: citations,
      duplicate_status: sources.length > 1 ? "merged" : "unique",
      merge_confidence: sources.length > 1 ? 0.95 : 0.65,
      merge_notes: [],
      source_confidence_signals: Object.fromEntries(sources.map((source) => [source, 0.75])),
      url: null
    }
  };
}

function analysisFor(kind: "kim" | "lee" | "park"): Analysis {
  if (kind === "kim") {
    return {
      trend_summary: "최근 5년간 자연어처리와 텍스트마이닝 연구가 반복되며, 최근에는 생성형 AI 기반 교육 피드백으로 확장되는 경향이 있습니다.",
      detailed_trend_summary: "김민준 교수님의 공개 논문 후보에서는 추천시스템과 텍스트마이닝 흐름이 확인됩니다. 최근에는 LLM과 학습자 피드백을 연결한 교육 AI 주제가 나타납니다. needs_review 논문은 보조 근거로만 반영했습니다.",
      recent_keywords: ["LLM", "교육 AI", "자연어처리", "학습자 피드백"],
      five_year_keywords: ["LLM", "텍스트마이닝", "학습분석", "교육 AI"],
      overall_keywords: ["자연어처리", "추천시스템", "교육 AI", "텍스트마이닝"],
      timeline: { "2016": ["추천시스템"], "2023": ["텍스트마이닝"], "2025": ["LLM", "교육 AI"] },
      trend_confidence: "medium",
      representative_papers: [{ id: 103, title: "디지털 도서관 추천을 위한 협업 필터링 모델", year: 2016, source_list: ["kci", "riss"], citation_signals: { kci: 32 }, match_status: "needs_review", label: "과거 대표 논문", why_read_this: "교수님의 기존 추천시스템 연구축을 이해하기 좋습니다." }],
      recent_important_papers: [{ id: 101, title: "LLM 기반 맞춤형 학습 피드백 서비스 연구", year: 2025, source_list: ["kci", "scienceon"], citation_signals: { kci: 4, scienceon: 5 }, match_status: "accepted", label: "최근 연구 논문", why_read_this: "최근 LLM 응용 방향을 파악하기 좋습니다." }],
      recent_papers: [{ id: 101, title: "LLM 기반 맞춤형 학습 피드백 서비스 연구", year: 2025, source_list: ["kci", "scienceon"], citation_signals: { kci: 4, scienceon: 5 }, match_status: "accepted", label: "최근 연구 논문" }],
      interest_related_papers: [],
      supporting_papers: [{ id: 102, title: "트랜스포머를 활용한 학습 성찰 텍스트 마이닝", year: 2023, source_list: ["dbpia"], citation_signals: { dbpia: 3 }, match_status: "needs_review", label: "보조 후보 논문" }],
      excluded_papers_count: 0,
      evidence_confidence: "medium",
      warnings: ["검증 필요 논문 일부 포함: needs_review 논문은 보조 근거로만 사용했습니다."]
    };
  }
  if (kind === "lee") {
    return {
      trend_summary: "의료 영상과 딥러닝 기반 임상 의사결정 지원 연구가 확인되며, 일부 동명이인 후보는 검증 대상으로 분리했습니다.",
      detailed_trend_summary: "이서연 교수님의 공개 후보에서는 흉부 CT와 딥러닝 기반 의료 영상 분석이 중심 신호로 나타납니다. 이름이 같은 다른 분야 논문은 낮은 신뢰도 후보로 보존했습니다.",
      recent_keywords: ["의료 영상", "딥러닝", "임상 의사결정 지원"],
      five_year_keywords: ["의료 영상", "딥러닝", "임상"],
      overall_keywords: ["의료 영상", "딥러닝", "임상 의사결정 지원"],
      timeline: { "2024": ["의료 영상", "딥러닝"] },
      trend_confidence: "medium",
      representative_papers: [{ id: 201, title: "흉부 CT 결절 탐지를 위한 딥러닝 기반 의료 영상 분석", year: 2024, source_list: ["kci", "dbpia"], citation_signals: { kci: 7, dbpia: 2 }, match_status: "accepted", label: "대표 논문 후보" }],
      recent_important_papers: [{ id: 201, title: "흉부 CT 결절 탐지를 위한 딥러닝 기반 의료 영상 분석", year: 2024, source_list: ["scienceon"], citation_signals: { scienceon: 4 }, match_status: "accepted", label: "최근 연구 논문" }],
      recent_papers: [],
      interest_related_papers: [],
      supporting_papers: [{ id: 202, title: "반도체 공정 최적화를 위한 플라즈마 시뮬레이션", year: 2022, source_list: ["riss"], citation_signals: { riss: null }, match_status: "weak_candidate", label: "보조 후보 논문" }],
      excluded_papers_count: 0,
      evidence_confidence: "medium",
      warnings: ["동명이인 가능성으로 검증 필요: 일부 논문 후보에서 소속/주제 근거가 약합니다."]
    };
  }
  return {
    trend_summary: "공개 논문 데이터는 제한적입니다. 공식 연구분야 기준으로 감염관리, 환자안전, 보건정보 분야를 중심으로 확인됩니다.",
    detailed_trend_summary: "박지훈 교수님의 공개 논문 후보는 많지 않습니다. 현재는 교수소개 페이지와 연구실 키워드를 중심으로 감염관리와 환자안전 주제를 참고할 수 있습니다.",
    recent_keywords: ["감염관리", "환자안전", "보건정보"],
    five_year_keywords: ["감염관리", "환자안전", "보건정보"],
    overall_keywords: ["환자안전", "감염관리", "보건정보"],
    timeline: { "2025": ["감염관리", "환자안전"] },
    trend_confidence: "low",
    representative_papers: [{ id: 301, title: "감염관리 실무를 위한 디지털 감시 대시보드", year: 2025, source_list: ["scienceon"], citation_signals: { scienceon: 1 }, match_status: "needs_review", label: "대표 논문 후보" }],
    recent_important_papers: [{ id: 301, title: "감염관리 실무를 위한 디지털 감시 대시보드", year: 2025, source_list: ["scienceon"], citation_signals: { scienceon: 1 }, match_status: "needs_review", label: "최근 연구 논문" }],
    recent_papers: [],
    interest_related_papers: [],
    supporting_papers: [],
    excluded_papers_count: 0,
    evidence_confidence: "low",
    warnings: ["공개 논문 데이터는 제한적입니다.", "현재 모집 주제는 컨택 시 확인이 필요합니다."]
  };
}

export const mockCrawlResponse: CrawlResponse = {
  department,
  professors: baseProfessors.map((professor) => ({ ...professor })),
  warnings: ["샘플 데이터로 표시 중입니다. 실제 크롤링 결과는 사용자가 확인한 뒤 논문 수집을 시작하세요."]
};

export const mockHarvestResponse: HarvestDepartmentResponse = {
  department,
  results: [
    result(baseProfessors[0], 9, 3, 1, 2, 0, 0, analysisFor("kim")),
    result(baseProfessors[1], 6, 2, 1, 0, 1, 0, analysisFor("lee")),
    result(baseProfessors[2], 3, 1, 0, 1, 0, 0, analysisFor("park"))
  ]
};

function result(professor: (typeof baseProfessors)[number], source: number, master: number, accepted: number, review: number, weak: number, rejected: number, analysis: Analysis) {
  return {
    professor,
    source_candidate_count: source,
    master_paper_count: master,
    accepted_count: accepted,
    needs_review_count: review,
    weak_candidate_count: weak,
    rejected_count: rejected,
    analysis_ready_count: accepted + review,
    review_candidate_count: review + weak,
    candidate_pool_count: accepted + review + weak,
    excluded_count: rejected,
    warning_count: analysis.warnings.length,
    usable_rate: master ? Math.round(((accepted + review) / master) * 1000) / 10 : 0,
    candidate_pool_rate: master ? Math.round(((accepted + review + weak) / master) * 1000) / 10 : 0,
    excluded_rate: master ? Math.round((rejected / master) * 1000) / 10 : 0,
    analysis
  };
}

export const mockCards: ProfessorCard[] = mockHarvestResponse.results.map((item) => ({
  ...item.professor,
  keywords: item.analysis.five_year_keywords.slice(0, 5),
  trend_summary: item.analysis.trend_summary,
  recent_keywords: item.analysis.recent_keywords,
  five_year_keywords: item.analysis.five_year_keywords,
  overall_keywords: item.analysis.overall_keywords,
  trend_confidence: item.analysis.trend_confidence,
  warnings: item.analysis.warnings,
  accepted_paper_count: item.accepted_count,
  needs_review_paper_count: item.needs_review_count,
  weak_candidate_count: item.weak_candidate_count,
  rejected_paper_count: item.rejected_count,
  source_coverage: sourceCoverage(item.professor.id)
}));

function sourceCoverage(id: number): Record<string, number> {
  if (id === 1) return { KCI: 3, DBpia: 1, RISS: 1, ScienceON: 1, Crossref: 2 };
  if (id === 2) return { KCI: 1, DBpia: 1, RISS: 1, ScienceON: 1 };
  return { DBpia: 1, ScienceON: 1, Crossref: 1 };
}

export const mockDetails: Record<number, ProfessorDetail> = {
  1: { ...baseProfessors[0], department_info: department, papers: kimPapers, analysis: analysisFor("kim") },
  2: { ...baseProfessors[1], department_info: department, papers: leePapers, analysis: analysisFor("lee") },
  3: { ...baseProfessors[2], department_info: department, papers: parkPapers, analysis: analysisFor("park") }
};

export function mockFit(professorId: number, userInterest: string): FitResult {
  if (professorId === 1) {
    return {
      fit_level: "중간",
      interpretation: `최근 연구는 LLM과 자연어처리 응용에는 가깝지만, '${userInterest}'의 세부 도메인은 컨택 시 확인이 필요합니다.`,
      matched_keywords: ["LLM", "교육 AI", "자연어처리", "학습자 피드백"],
      related_papers: [{ id: 101, title: "LLM 기반 맞춤형 학습 피드백 서비스 연구", year: 2025, source_list: ["kci", "scienceon"], citation_signals: { kci: 4, scienceon: 5 }, match_status: "accepted", connection_reason: "LLM/교육 서비스 키워드와 직접 연결됩니다.", why_read_this: "관심 주제와 가장 가까운 최근 논문입니다." }],
      check_points: ["교육 도메인 프로젝트가 현재 진행 중인지 확인", "석사 주제로 진행 가능한 범위 확인", "필요한 NLP/서비스 구현 경험 확인"],
      evidence_confidence: "medium"
    };
  }
  return {
    fit_level: "판단 보류",
    interpretation: "공개 논문 데이터가 제한적입니다. 연구실 소개와 현재 프로젝트를 중심으로 컨택 시 확인이 필요합니다.",
    matched_keywords: [],
    related_papers: [],
    check_points: ["현재 모집 주제 확인", "관련 프로젝트 진행 여부 확인", "필요한 선수지식 확인"],
    evidence_confidence: "low"
  };
}

export function mockContactCard(professorId: number, userInterest: string): ContactCard {
  const detail = mockDetails[professorId] ?? mockDetails[1];
  const fit = mockFit(professorId, userInterest);
  const reading = [
    ...(detail.analysis.representative_papers.slice(0, 1).map((paper) => ({ id: paper.id, title: paper.title, year: paper.year, venue: paper.venue, why_read: paper.why_read_this ?? "교수님의 기존 연구축을 이해하기 좋은 대표 논문입니다.", category: "대표 논문" }))),
    ...((detail.analysis.recent_important_papers ?? detail.analysis.recent_papers).slice(0, 1).map((paper) => ({ id: paper.id, title: paper.title, year: paper.year, venue: paper.venue, why_read: paper.why_read_this ?? "최근 연구 방향을 파악하기 좋습니다.", category: "최근 연구 논문" }))),
    ...(fit.related_papers.slice(0, 1).map((paper) => ({ id: paper.id, title: paper.title, year: paper.year, venue: paper.venue, why_read: paper.why_read_this ?? "관심 주제와 가장 직접적으로 연결됩니다.", category: "관심주제 관련 논문" })))
  ];

  return {
    professor_id: professorId,
    professor_name: detail.name,
    reading_list: reading.slice(0, 3),
    questions: [
      "현재 연구실에서 해당 주제를 석사 주제로 진행할 수 있나요?",
      "관련 프로젝트나 과제가 진행 중인가요?",
      "학부 단계에서 준비하면 좋은 선수지식은 무엇인가요?",
      "논문 중심 연구와 프로젝트 중심 연구의 비중은 어느 정도인가요?",
      "학부연구생 또는 예비 대학원생이 참여할 수 있는 주제가 있나요?"
    ],
    email_points: detail.analysis.five_year_keywords.slice(0, 3).map((keyword) => `${keyword} 관련 공개 연구 흐름을 보고 관심을 갖게 되었음을 언급`),
    check_points: fit.check_points,
    evidence_confidence: detail.analysis.evidence_confidence
  };
}
