export type Confidence = "high" | "medium" | "low";
export type MatchStatus = "accepted" | "needs_review" | "weak_candidate" | "rejected";
export type AnalysisType = "paper_based" | "emerging_lab" | "data_limited" | string;

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
  warnings: string[];
  accepted_count?: number;
  needs_review_count?: number;
  rejected_count?: number;
  source_candidate_count?: number;
  master_paper_count?: number;
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

export type Analysis = {
  trend_summary: string;
  recent_keywords: string[];
  five_year_keywords: string[];
  overall_keywords: string[];
  timeline: Record<string, string[]>;
  representative_papers: AnalysisPaper[];
  recent_papers: AnalysisPaper[];
  evidence_confidence: Confidence | string;
  warnings: string[];
};

export type AnalysisPaper = {
  id?: number;
  title?: string;
  year?: number | null;
  venue?: string | null;
  citation_signals?: Record<string, number | null>;
  match_status?: MatchStatus;
  label?: string;
  reason?: string;
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
  analysis: Analysis;
};

export type HarvestDepartmentResponse = {
  department: Department;
  results: HarvestProfessorResult[];
};

export type FitResult = {
  fit_level: "높음" | "중간~높음" | "중간" | "낮음" | "판단 보류" | string;
  interpretation: string;
  matched_keywords: string[];
  related_papers: Array<{
    id?: number;
    title?: string;
    year?: number | null;
    venue?: string | null;
    match_status?: MatchStatus;
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
