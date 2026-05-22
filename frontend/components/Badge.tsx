import type { AnalysisType, Confidence, MatchStatus } from "@/lib/types";

type BadgeTone = "gold" | "green" | "purple" | "muted" | "dark";

const toneClass: Record<BadgeTone, string> = {
  gold: "border-gold/30 bg-gold/15 text-gold",
  green: "border-green/30 bg-green/15 text-green",
  purple: "border-purple/30 bg-purple/15 text-purple",
  muted: "border-warm-gray/25 bg-warm-gray/10 text-warm-gray",
  dark: "border-warm-gray/20 bg-dark-green text-white"
};

export function Badge({ children, tone = "muted" }: { children: React.ReactNode; tone?: BadgeTone }) {
  return (
    <span className={`inline-flex items-center whitespace-nowrap rounded-full border px-2.5 py-1 text-xs font-semibold ${toneClass[tone]}`}>
      {children}
    </span>
  );
}

export function MatchBadge({ status }: { status?: MatchStatus | string }) {
  if (status === "accepted") return <Badge tone="green">분석 사용 가능</Badge>;
  if (status === "needs_review") return <Badge tone="gold">검증 필요</Badge>;
  if (status === "weak_candidate") return <Badge tone="muted">낮은 신뢰도 후보</Badge>;
  if (status === "rejected") return <Badge tone="dark">분석 제외</Badge>;
  return <Badge>확인 전</Badge>;
}

export function AnalysisTypeBadge({ type }: { type?: AnalysisType }) {
  if (type === "domestic_db_based" || type === "paper_based") return <Badge tone="purple">국내 학술 DB 기반</Badge>;
  if (type === "emerging_lab") return <Badge tone="gold">Emerging Lab</Badge>;
  if (type === "data_limited") return <Badge tone="muted">공개 데이터 제한</Badge>;
  return <Badge tone="muted">분석 준비 중</Badge>;
}

export function ConfidenceBadge({ confidence }: { confidence?: Confidence | string }) {
  if (confidence === "high") return <Badge tone="green">근거 신뢰도 높음</Badge>;
  if (confidence === "medium") return <Badge tone="purple">근거 신뢰도 중간</Badge>;
  return <Badge tone="gold">근거 신뢰도 낮음</Badge>;
}

export function SourceBadge({ source }: { source: string }) {
  const normalized = source.toLowerCase();
  const labels: Record<string, string> = {
    kci: "KCI",
    riss: "RISS",
    dbpia: "DBpia",
    scienceon: "ScienceON",
    crossref: "Crossref",
    dblp: "DBLP",
    professor_lab_page_publication: "공식페이지",
    openalex: "OpenAlex"
  };
  const tone: BadgeTone =
    normalized === "kci" || normalized === "professor_lab_page_publication"
      ? "green"
      : normalized === "crossref"
        ? "purple"
        : "muted";
  return <Badge tone={tone}>{labels[normalized] ?? source}</Badge>;
}
