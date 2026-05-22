import type { AnalysisType, Confidence, MatchStatus } from "@/lib/types";

type BadgeTone = "blue" | "green" | "amber" | "slate" | "rose" | "navy";

const toneClass: Record<BadgeTone, string> = {
  blue: "border-bluepoint/25 bg-bluepoint/10 text-navy-800",
  green: "border-emerald-500/25 bg-emerald-50 text-emerald-800",
  amber: "border-amber-500/30 bg-amber-50 text-amber-800",
  slate: "border-slate-300 bg-slate-100 text-slate-700",
  rose: "border-rose-500/25 bg-rose-50 text-rose-800",
  navy: "border-navy-800/20 bg-navy-900 text-white"
};

export function Badge({
  children,
  tone = "slate"
}: {
  children: React.ReactNode;
  tone?: BadgeTone;
}) {
  return (
    <span className={`inline-flex items-center whitespace-nowrap rounded-full border px-2.5 py-1 text-xs font-semibold ${toneClass[tone]}`}>
      {children}
    </span>
  );
}

export function MatchBadge({ status }: { status?: MatchStatus | string }) {
  if (status === "accepted") return <Badge tone="green">accepted</Badge>;
  if (status === "needs_review") return <Badge tone="amber">검증 필요</Badge>;
  if (status === "rejected") return <Badge tone="rose">rejected</Badge>;
  if (status === "weak_candidate") return <Badge tone="slate">약한 후보</Badge>;
  return <Badge>확인 전</Badge>;
}

export function AnalysisTypeBadge({ type }: { type?: AnalysisType }) {
  if (type === "paper_based") return <Badge tone="blue">논문 기반</Badge>;
  if (type === "emerging_lab") return <Badge tone="amber">Emerging Lab</Badge>;
  if (type === "data_limited") return <Badge tone="slate">공개 데이터 제한</Badge>;
  return <Badge tone="slate">분석 준비 중</Badge>;
}

export function ConfidenceBadge({ confidence }: { confidence?: Confidence | string }) {
  if (confidence === "high") return <Badge tone="green">근거 신뢰도 높음</Badge>;
  if (confidence === "medium") return <Badge tone="blue">근거 신뢰도 중간</Badge>;
  return <Badge tone="amber">근거 신뢰도 낮음</Badge>;
}

export function SourceBadge({ source }: { source: string }) {
  const normalized = source.toLowerCase();
  const label =
    normalized === "kci"
      ? "KCI"
      : normalized === "openalex"
        ? "OpenAlex"
        : normalized === "crossref"
          ? "Crossref"
          : normalized === "dblp"
            ? "DBLP"
            : normalized === "riss"
              ? "RISS"
              : normalized === "scienceon"
                ? "ScienceON"
                : normalized === "dbpia"
                  ? "DBpia"
                  : source;
  return <Badge tone={normalized === "openalex" ? "blue" : normalized === "kci" ? "green" : "slate"}>{label}</Badge>;
}
