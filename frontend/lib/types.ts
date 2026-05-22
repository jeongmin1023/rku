export type Confidence = "high" | "medium" | "low";
export type MatchStatus = "accepted" | "needs_review" | "weak_candidate" | "rejected";
export type AnalysisType = "paper_based" | "domestic_db_based" | "emerging_lab" | "data_limited" | string;

export type Department = {
  id: number;
  university: string;
  department: string;
  source_url: string;
  created_at: string;
};

export type Professor = {
  id: number;
  department_id: number;
  name: string;
  english_name?: string | null;
  title?: string | null;
  university: string;
  department: string;
  lab_name?: string | null;
  email?: string | null;
  profile_url?: string | null;
  lab_url?: string | null;
  official_keywords?: string | null;
  source_url: string;
  extraction_confidence: number;
  analysis_type: AnalysisType;
  evidence_confidence: Confidence | string;
  created_at: string;
};

export type ProfessorCard = Professor & {
  keywords: string[];
  trend_summary?: string | null;
  recent_keywords?: string[];
  five_year_keywords?: string[];
  overall_keywords?: string[];
  trend_confidence?: Confidence | string;
  warnings: string[];
  accepted_paper_count?: number;
  needs_review_paper_count?: number;
  weak_candidate_count?: number;
  rejected_paper_count?: number;
  source_coverage?: Record<string, number>;
  accepted_count?: number;
  needs_review_count?: number;
  rejected_count?: number;
  source_candidate_count?: number;
  master_paper_count?: number;
  analysis_ready_count?: number;
  review_candidate_count?: number;
  candidate_pool_count?: number;
  excluded_count?: number;
  warning_count?: number;
  usable_rate?: number;
  candidate_pool_rate?: number;
  excluded_rate?: number;
};

export type CrawlResponse = {
  department: Department;
  professors: Professor[];
  warnings: string[];
};

export type ConfirmProfessor = {
  name: string;
  english_name?: string | null;
  title?: string | null;
  lab_name?: string | null;
  email?: string | null;
  profile_url?: string | null;
  lab_url?: string | null;
  official_keywords?: string | null;
  extraction_confidence: number;
  excluded: boolean;
};

export type MasterPaper = {
  id: number;
  title_ko?: string | null;
  title_en?: string | null;
  display_title: string;
  authors: string[];
  author_affiliations: string[];
  year?: number | null;
  venue?: string | null;
  doi?: string | null;
  uci?: string | null;
  abstract?: string | null;
  keywords: string[];
  source_list: string[];
  source_ids: Record<string, string[]>;
  citation_signals: Record<string, number | null>;
  duplicate_status: string;
  merge_confidence?: number;
  merge_notes?: string[];
  source_confidence_signals?: Record<string, number>;
  url?: string | null;
};

export type ProfessorPaper = {
  id: number;
  master_paper: MasterPaper;
  match_score: number;
  match_status: MatchStatus;
  author_role?: string | null;
  evidence_notes: Record<string, unknown>;
  warnings: string[];
};

export type AnalysisPaper = {
  id?: number;
  title?: string;
  year?: number | null;
  venue?: string | null;
  citation_signals?: Record<string, number | null>;
  source_list?: string[];
  match_status?: MatchStatus;
  author_role?: string | null;
  category?: string;
  label?: string;
  reason?: string;
  category_reason?: string;
  why_read_this?: string;
};

export type Analysis = {
  trend_summary: string;
  detailed_trend_summary?: string | null;
  recent_keywords: string[];
  five_year_keywords: string[];
  overall_keywords: string[];
  timeline: Record<string, string[]>;
  trend_confidence?: Confidence | string;
  representative_papers: AnalysisPaper[];
  recent_important_papers?: AnalysisPaper[];
  recent_papers: AnalysisPaper[];
  interest_related_papers?: AnalysisPaper[];
  supporting_papers?: AnalysisPaper[];
  excluded_papers_count?: number;
  evidence_confidence: Confidence | string;
  warnings: string[];
};

export type ProfessorDetail = Professor & {
  department_info: Department;
  papers: ProfessorPaper[];
  analysis: Analysis;
};

export type HarvestProfessorResult = {
  professor: Professor;
  source_candidate_count: number;
  master_paper_count: number;
  accepted_count: number;
  needs_review_count: number;
  weak_candidate_count: number;
  rejected_count: number;
  analysis_ready_count: number;
  review_candidate_count: number;
  candidate_pool_count: number;
  excluded_count: number;
  warning_count: number;
  usable_rate: number;
  candidate_pool_rate: number;
  excluded_rate: number;
  analysis: Analysis;
};

export type HarvestDepartmentResponse = {
  department: Department;
  results: HarvestProfessorResult[];
};

export type FitRequest = {
  user_interest: string;
};

export type FitResult = {
  fit_level: "높음" | "중간~높음" | "중간" | "낮음" | "판단 보류" | "중간, 확인 필요" | string;
  interpretation: string;
  matched_keywords: string[];
  related_papers: Array<AnalysisPaper & {
    connection_reason?: string;
    connection_signal?: number;
  }>;
  check_points: string[];
  evidence_confidence: Confidence | string;
};

export type ContactCard = {
  professor_id: number;
  professor_name: string;
  reading_list: Array<{
    id?: number;
    title?: string;
    year?: number | null;
    venue?: string | null;
    why_read: string;
    category: string;
  }>;
  questions: string[];
  email_points: string[];
  check_points: string[];
  evidence_confidence: Confidence | string;
};

export type AppStep = "onboarding" | "review" | "harvesting" | "cards";
