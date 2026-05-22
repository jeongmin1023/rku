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
    analysis_type: "paper_based",
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
    analysis_type: "data_limited",
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
  {
    id: 101,
    match_score: 0.858,
    match_status: "accepted",
    author_role: "first_author",
    warnings: [],
    evidence_notes: {
      name_match: "이름과 영문명이 저자명과 일치",
      affiliation_match: "학교명이 KCI/OpenAlex 소속에 감지",
      topic_match: ["LLM", "자연어처리", "교육 AI"],
      source_agreement: ["kci", "openalex", "crossref"]
    },
    master_paper: {
      id: 101,
      title_ko: "LLM 기반 맞춤형 학습 피드백 서비스 연구",
      title_en: "Large Language Model Assisted Feedback for Personalized Learning Services",
      display_title: "Large Language Model Assisted Feedback for Personalized Learning Services",
      authors: ["김민준", "Minjun Kim", "최아리"],
      author_affiliations: ["샘플대학교 컴퓨터공학과", "Sample University Department of Computer Science"],
      year: 2025,
      venue: "Journal of Educational AI",
      doi: "10.5555/labfit.2025.001",
      uci: "G704-SAMPLE.2025.001",
      abstract: "LLM based educational services use natural language processing, learner feedback, and recommender systems.",
      keywords: ["LLM", "자연어처리", "교육 AI", "추천시스템"],
      source_list: ["kci", "openalex", "crossref"],
      source_ids: { kci: ["KCI-KIM-2025-001"], openalex: ["WKIM2025001"], crossref: ["CR-KIM-2025-001"] },
      citation_signals: { kci: 4, openalex: 21, crossref: 0 },
      duplicate_status: "merged",
      url: "https://doi.org/10.5555/labfit.2025.001"
    }
  },
  {
    id: 102,
    match_score: 0.752,
    match_status: "needs_review",
    author_role: "first_author",
    warnings: ["영문 제목 표현 차이가 있어 병합 근거 확인이 필요합니다."],
    evidence_notes: {
      name_match: "영문명 일치",
      affiliation_match: "학교명 감지",
      topic_match: ["텍스트마이닝", "Transformer"],
      source_agreement: ["kci", "openalex"]
    },
    master_paper: {
      id: 102,
      display_title: "Text Mining of Student Reflection Data with Transformer Models",
      title_ko: "트랜스포머 기반 학습 성찰 텍스트마이닝",
      title_en: "Text Mining of Student Reflection Data with Transformer Models",
      authors: ["김민준", "Minjun Kim", "최아리", "정하늘"],
      author_affiliations: ["샘플대학교 컴퓨터공학과"],
      year: 2023,
      venue: "Learning Analytics Review",
      doi: null,
      uci: "G704-SAMPLE.2023.002",
      abstract: "Transformer models and text mining are applied to student reflection data for learning analytics.",
      keywords: ["텍스트마이닝", "Transformer", "학습분석", "자연어처리"],
      source_list: ["kci", "openalex"],
      source_ids: { kci: ["KCI-KIM-2023-002"], openalex: ["WKIM2023002"] },
      citation_signals: { kci: 9, openalex: 25 },
      duplicate_status: "merged",
      url: null
    }
  },
  {
    id: 103,
    match_score: 0.742,
    match_status: "needs_review",
    author_role: "last_author",
    warnings: ["과거 논문이며 현재 연구 방향과의 연결은 보조 근거로만 확인하세요."],
    evidence_notes: {
      name_match: "이니셜 표기와 유사",
      affiliation_match: "학교명 감지",
      topic_match: ["추천시스템"],
      source_agreement: ["kci", "openalex", "crossref"]
    },
    master_paper: {
      id: 103,
      display_title: "Collaborative Filtering for Digital Library Recommendation",
      title_ko: "디지털 도서관 추천을 위한 협업 필터링 모델",
      title_en: "Collaborative Filtering for Digital Library Recommendation",
      authors: ["김민준", "Minjun Kim"],
      author_affiliations: ["샘플대학교 컴퓨터공학과"],
      year: 2016,
      venue: "Information Systems",
      doi: "10.5555/labfit.2016.003",
      uci: "G704-SAMPLE.2016.003",
      abstract: "A recommender system for digital libraries is proposed with collaborative filtering and user modeling.",
      keywords: ["추천시스템", "협업 필터링", "정보검색"],
      source_list: ["kci", "openalex", "crossref"],
      source_ids: { kci: ["KCI-KIM-2016-003"], openalex: ["WKIM2016003"], crossref: ["CR-KIM-2016-003"] },
      citation_signals: { kci: 32, openalex: 111, crossref: 0 },
      duplicate_status: "merged",
      url: "https://doi.org/10.5555/labfit.2016.003"
    }
  }
];

const leePapers: ProfessorPaper[] = [
  {
    id: 201,
    match_score: 0.842,
    match_status: "accepted",
    author_role: "first_author",
    warnings: [],
    evidence_notes: {
      name_match: "영문명 일치",
      affiliation_match: "학교명 감지",
      topic_match: ["의료 영상", "딥러닝"],
      source_agreement: ["kci", "openalex", "crossref"]
    },
    master_paper: {
      id: 201,
      display_title: "Deep Learning Based Pulmonary Nodule Detection in Chest CT",
      title_ko: "흉부 CT 결절 탐지를 위한 딥러닝 기반 의료 영상 분석",
      title_en: "Deep Learning Based Pulmonary Nodule Detection in Chest CT",
      authors: ["이서연", "Seoyeon Lee", "한도윤"],
      author_affiliations: ["샘플대학교 의공학과", "Sample University Biomedical Engineering"],
      year: 2024,
      venue: "Medical Image Analysis Practice",
      doi: "10.5555/labfit.2024.101",
      uci: "G704-SAMPLE.2024.101",
      abstract: "Medical imaging and deep learning support pulmonary nodule detection and clinical decision support.",
      keywords: ["의료 영상", "딥러닝", "임상 의사결정 지원"],
      source_list: ["kci", "openalex", "crossref"],
      source_ids: { kci: ["KCI-LEE-2024-001"], openalex: ["WLEE2024101"], crossref: ["CR-LEE-2024-101"] },
      citation_signals: { kci: 7, openalex: 31, crossref: 0 },
      duplicate_status: "merged",
      url: "https://doi.org/10.5555/labfit.2024.101"
    }
  },
  {
    id: 202,
    match_score: 0.39,
    match_status: "rejected",
    author_role: "first_author",
    warnings: ["이름은 유사하지만 현재 학교/학과 소속과 연구 주제가 다릅니다."],
    evidence_notes: {
      name_match: "영문명 유사",
      affiliation_match: "다른대학교 소속",
      topic_match: [],
      source_agreement: ["kci", "openalex"]
    },
    master_paper: {
      id: 202,
      display_title: "Plasma Simulation for Semiconductor Process Optimization",
      title_ko: "반도체 공정 최적화를 위한 플라즈마 시뮬레이션",
      title_en: "Plasma Simulation for Semiconductor Process Optimization",
      authors: ["이서연", "Seoyeon Lee", "Michael Brown"],
      author_affiliations: ["다른대학교 전자공학과", "Other University Department of Electrical Engineering"],
      year: 2022,
      venue: "Semiconductor Engineering Letters",
      doi: "10.5555/other.2022.404",
      uci: "G704-OTHER.2022.404",
      abstract: "Plasma simulation is used for semiconductor process optimization.",
      keywords: ["반도체", "플라즈마", "공정 최적화"],
      source_list: ["kci", "openalex"],
      source_ids: { kci: ["KCI-CONTAMINATION-001"], openalex: ["WLEE2022404"] },
      citation_signals: { kci: 19, openalex: 44 },
      duplicate_status: "merged",
      url: null
    }
  }
];

const parkPapers: ProfessorPaper[] = [
  {
    id: 301,
    match_score: 0.82,
    match_status: "accepted",
    author_role: "first_author",
    warnings: ["공개 논문 수가 적어 연구실 소개와 현재 프로젝트 확인이 필요합니다."],
    evidence_notes: {
      name_match: "영문명 일치",
      affiliation_match: "학교명 감지",
      topic_match: ["감염관리", "환자안전"],
      source_agreement: ["kci", "openalex", "crossref"]
    },
    master_paper: {
      id: 301,
      display_title: "Digital Surveillance Dashboard for Infection Control Practice",
      title_ko: "감염관리 실무를 위한 디지털 감시 대시보드",
      title_en: "Digital Surveillance Dashboard for Infection Control Practice",
      authors: ["박지훈", "Jihoon Park", "오수민"],
      author_affiliations: ["샘플대학교 간호학과", "Sample University Nursing"],
      year: 2025,
      venue: "Journal of Patient Safety Informatics",
      doi: "10.5555/labfit.2025.301",
      uci: "G704-SAMPLE.2025.301",
      abstract: "A dashboard for infection control and patient safety is evaluated in hospital workflows.",
      keywords: ["감염관리", "환자안전", "보건정보"],
      source_list: ["kci", "openalex", "crossref"],
      source_ids: { kci: ["KCI-PARK-2025-001"], openalex: ["WPARK2025301"], crossref: ["CR-PARK-2025-301"] },
      citation_signals: { kci: 1, openalex: 5, crossref: 0 },
      duplicate_status: "merged",
      url: "https://doi.org/10.5555/labfit.2025.301"
    }
  }
];

function analysisFor(kind: "kim" | "lee" | "park"): Analysis {
  if (kind === "kim") {
    return {
      trend_summary: "최근 연구에서는 LLM, 자연어처리, 교육 AI 관련 키워드가 반복적으로 나타나며, 과거 추천시스템 연구와 연결됩니다. 검증 필요 논문 일부가 보조 근거로 포함되었습니다.",
      recent_keywords: ["LLM", "교육 AI", "자연어처리", "학습분석"],
      five_year_keywords: ["LLM", "텍스트마이닝", "Transformer", "추천시스템"],
      overall_keywords: ["자연어처리", "추천시스템", "교육 AI", "학습분석", "정보검색"],
      timeline: {
        "2016": ["추천시스템", "협업 필터링"],
        "2023": ["텍스트마이닝", "Transformer"],
        "2025": ["LLM", "교육 AI"]
      },
      representative_papers: [
        { id: 103, title: "Collaborative Filtering for Digital Library Recommendation", year: 2016, venue: "Information Systems", citation_signals: { kci: 32, openalex: 111 }, match_status: "needs_review", label: "과거 대표 논문", reason: "인용 신호와 추천시스템 키워드 연결성이 함께 감지됩니다." },
        { id: 101, title: "Large Language Model Assisted Feedback for Personalized Learning Services", year: 2025, venue: "Journal of Educational AI", citation_signals: { kci: 4, openalex: 21 }, match_status: "accepted", label: "대표 논문 후보", reason: "최근 연구 방향과 공식 키워드가 잘 맞닿아 있습니다." }
      ],
      recent_papers: [
        { id: 101, title: "Large Language Model Assisted Feedback for Personalized Learning Services", year: 2025, venue: "Journal of Educational AI", citation_signals: { kci: 4, openalex: 21 }, match_status: "accepted", label: "최근 연구 흐름", reason: "최근 연도와 관심 주제 연결성이 큽니다." },
        { id: 102, title: "Text Mining of Student Reflection Data with Transformer Models", year: 2023, venue: "Learning Analytics Review", citation_signals: { kci: 9, openalex: 25 }, match_status: "needs_review", label: "최근 연구 흐름", reason: "텍스트마이닝과 학습분석 흐름을 보여줍니다." }
      ],
      evidence_confidence: "medium",
      warnings: ["검증 필요 논문 일부 포함: needs_review 논문은 보조 근거로만 사용했습니다."]
    };
  }

  if (kind === "lee") {
    return {
      trend_summary: "의료 영상과 딥러닝 기반 임상 의사결정 지원 흐름이 보입니다. 이름이 같은 오염 후보가 있어 소속과 주제 근거를 함께 확인했습니다.",
      recent_keywords: ["의료 영상", "딥러닝", "임상 의사결정 지원"],
      five_year_keywords: ["의료 영상", "딥러닝", "Radiology"],
      overall_keywords: ["의료 영상", "딥러닝", "임상 의사결정 지원"],
      timeline: {
        "2024": ["의료 영상", "딥러닝"]
      },
      representative_papers: [
        { id: 201, title: "Deep Learning Based Pulmonary Nodule Detection in Chest CT", year: 2024, venue: "Medical Image Analysis Practice", citation_signals: { kci: 7, openalex: 31 }, match_status: "accepted", label: "대표 논문 후보", reason: "공식 연구 키워드와 소속 근거가 함께 감지됩니다." }
      ],
      recent_papers: [
        { id: 201, title: "Deep Learning Based Pulmonary Nodule Detection in Chest CT", year: 2024, venue: "Medical Image Analysis Practice", citation_signals: { kci: 7, openalex: 31 }, match_status: "accepted", label: "최근 연구 흐름", reason: "최근 의료 영상 연구 방향을 보여줍니다." }
      ],
      evidence_confidence: "medium",
      warnings: ["오염 가능성이 있는 논문은 기본 목록에서 제외했습니다.", "공개 논문 데이터는 추가 확인이 필요합니다."]
    };
  }

  return {
    trend_summary: "공개 논문 데이터는 제한적입니다. 현재는 감염관리, 환자안전, 보건정보 관련 공개 정보와 교수소개 페이지 키워드를 중심으로 연구 방향을 확인할 수 있습니다.",
    recent_keywords: ["감염관리", "환자안전", "보건정보"],
    five_year_keywords: ["감염관리", "환자안전", "보건정보"],
    overall_keywords: ["환자안전", "감염관리", "보건정보"],
    timeline: {
      "2025": ["감염관리", "환자안전"]
    },
    representative_papers: [
      { id: 301, title: "Digital Surveillance Dashboard for Infection Control Practice", year: 2025, venue: "Journal of Patient Safety Informatics", citation_signals: { kci: 1, openalex: 5 }, match_status: "accepted", label: "대표 논문 후보", reason: "신임 연구실의 공개 연구 방향을 보여주는 근거입니다." }
    ],
    recent_papers: [
      { id: 301, title: "Digital Surveillance Dashboard for Infection Control Practice", year: 2025, venue: "Journal of Patient Safety Informatics", citation_signals: { kci: 1, openalex: 5 }, match_status: "accepted", label: "최근 연구 흐름", reason: "최근 공개 논문이자 연구실 키워드와 연결됩니다." }
    ],
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
    { professor: baseProfessors[0], source_candidate_count: 9, master_paper_count: 3, accepted_count: 1, needs_review_count: 2, weak_candidate_count: 0, rejected_count: 0, analysis: analysisFor("kim") },
    { professor: baseProfessors[1], source_candidate_count: 6, master_paper_count: 2, accepted_count: 1, needs_review_count: 0, weak_candidate_count: 0, rejected_count: 1, analysis: analysisFor("lee") },
    { professor: baseProfessors[2], source_candidate_count: 3, master_paper_count: 1, accepted_count: 1, needs_review_count: 0, weak_candidate_count: 0, rejected_count: 0, analysis: analysisFor("park") }
  ]
};

export const mockCards: ProfessorCard[] = mockHarvestResponse.results.map((result, index) => ({
  ...result.professor,
  keywords: result.analysis.five_year_keywords.slice(0, 5),
  trend_summary: result.analysis.trend_summary,
  warnings: result.analysis.warnings,
  source_candidate_count: result.source_candidate_count,
  master_paper_count: result.master_paper_count,
  accepted_count: result.accepted_count,
  needs_review_count: result.needs_review_count,
  rejected_count: result.rejected_count,
  analysis_type: index === 0 ? "paper_based" : index === 1 ? "data_limited" : "emerging_lab",
  evidence_confidence: result.analysis.evidence_confidence
}));

export const mockDetails: Record<number, ProfessorDetail> = {
  1: { ...baseProfessors[0], department_info: department, papers: kimPapers.filter((paper) => paper.match_status !== "rejected"), analysis: analysisFor("kim") },
  2: { ...baseProfessors[1], department_info: department, papers: leePapers.filter((paper) => paper.match_status !== "rejected"), analysis: analysisFor("lee") },
  3: { ...baseProfessors[2], department_info: department, papers: parkPapers, analysis: analysisFor("park") }
};

export function mockFit(professorId: number, userInterest: string): FitResult {
  if (professorId === 1) {
    return {
      fit_level: "중간",
      interpretation: `이 교수님의 최근 연구는 LLM과 자연어처리 응용에는 가깝지만, '${userInterest}'의 도메인 적용 가능성은 컨택 시 확인이 필요합니다.`,
      matched_keywords: ["LLM", "교육 AI", "자연어처리", "학습분석"],
      related_papers: [
        { id: 101, title: "Large Language Model Assisted Feedback for Personalized Learning Services", year: 2025, venue: "Journal of Educational AI", match_status: "accepted", connection_reason: "관심 주제의 LLM/교육 서비스 키워드와 직접 연결됩니다." }
      ],
      check_points: ["교육 도메인 프로젝트가 현재 진행 중인지 확인", "석사 주제로 진행 가능한 세부 범위 확인", "필요한 NLP/웹서비스 구현 경험 확인"],
      evidence_confidence: "medium"
    };
  }
  if (professorId === 2) {
    return {
      fit_level: "판단 보류",
      interpretation: `공개 논문 기준으로 '${userInterest}'와 직접 연결되는 근거는 제한적입니다. 의료 영상 AI와 연결될 수 있는지 연구실 프로젝트를 확인하는 편이 좋습니다.`,
      matched_keywords: ["딥러닝", "의료 영상"],
      related_papers: [],
      check_points: ["관심 주제가 의료 영상 데이터와 연결될 수 있는지 확인", "임상 협업 프로젝트 여부 확인"],
      evidence_confidence: "medium"
    };
  }
  return {
    fit_level: "판단 보류",
    interpretation: "공개 논문 데이터가 제한적입니다. 연구실 소개, 강의 과목, 현재 프로젝트를 중심으로 컨택 전 확인이 필요합니다.",
    matched_keywords: ["감염관리", "환자안전", "보건정보"],
    related_papers: [],
    check_points: ["현재 모집 주제 확인", "보건정보 프로젝트 참여 가능성 확인", "필요한 선수지식 확인"],
    evidence_confidence: "low"
  };
}

export function mockContactCard(professorId: number, userInterest: string): ContactCard {
  const detail = mockDetails[professorId] ?? mockDetails[1];
  const fit = mockFit(professorId, userInterest);
  const reading = [
    ...(detail.analysis.representative_papers.slice(0, 1).map((paper) => ({ id: paper.id, title: paper.title, year: paper.year, venue: paper.venue, why_read: "연구실의 핵심 연구 흐름을 파악하기 위한 출발점입니다.", category: "대표 논문" }))),
    ...(detail.analysis.recent_papers.slice(0, 1).map((paper) => ({ id: paper.id, title: paper.title, year: paper.year, venue: paper.venue, why_read: "최근 연구 방향과 사용 기술 변화를 확인하기 좋습니다.", category: "최근 논문" }))),
    ...(fit.related_papers.slice(0, 1).map((paper) => ({ id: paper.id, title: paper.title, year: paper.year, venue: paper.venue, why_read: "내 관심 주제와 맞닿는 부분을 컨택 메일에 구체적으로 언급할 수 있습니다.", category: "관심 주제 관련 논문" })))
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
    email_points: detail.analysis.five_year_keywords.slice(0, 3).map((keyword) => `${keyword} 관련 공개 연구 흐름을 보고 관심을 갖게 되었다고 구체적으로 언급`),
    check_points: fit.check_points,
    evidence_confidence: detail.analysis.evidence_confidence
  };
}
