import { ChevronRight, GitCompare } from "lucide-react";

import { AnalysisTypeBadge, Badge, ConfidenceBadge } from "@/components/Badge";
import { EmptyState, SectionTitle } from "@/components/StateBlocks";
import type { ProfessorCard } from "@/lib/types";

type FilterKey =
  | "all"
  | "interest"
  | "recent"
  | "sufficient"
  | "limited"
  | "emerging";

const filters: Array<{ key: FilterKey; label: string }> = [
  { key: "all", label: "전체" },
  { key: "interest", label: "내 관심 주제와 가까움" },
  { key: "recent", label: "최근 논문 있음" },
  { key: "sufficient", label: "논문 데이터 충분" },
  { key: "limited", label: "공개 데이터 제한" },
  { key: "emerging", label: "Emerging Lab" },
];

export function ProfessorCards({
  cards,
  filter,
  onFilterChange,
  onOpenDetail,
  compareIds,
  onToggleCompare,
  userInterest,
}: {
  cards: ProfessorCard[];
  filter: FilterKey;
  onFilterChange: (filter: FilterKey) => void;
  onOpenDetail: (id: number) => void;
  compareIds: number[];
  onToggleCompare: (id: number) => void;
  userInterest: string;
}) {
  const filtered = cards.filter((card) => {
    if (filter === "all") return true;

    if (filter === "interest") {
      const interestTokens = userInterest
        .split(/[,\s]+/)
        .map((token) => token.trim().toLowerCase())
        .filter(Boolean);

      if (!interestTokens.length) return true;

      const haystack = [
        ...(card.keywords ?? []),
        ...(card.recent_keywords ?? []),
        ...(card.five_year_keywords ?? []),
        ...(card.overall_keywords ?? []),
        card.trend_summary ?? "",
        card.official_keywords ?? "",
      ]
        .join(" ")
        .toLowerCase();

      return interestTokens.some((token) => haystack.includes(token));
    }

    if (filter === "recent") {
      return (
        (card.recent_keywords?.length ?? 0) > 0 ||
        (card.accepted_paper_count ?? card.accepted_count ?? 0) > 0
      );
    }

    if (filter === "sufficient") {
      return (
        (card.accepted_paper_count ?? card.accepted_count ?? 0) >= 3 ||
        card.evidence_confidence === "high"
      );
    }

    if (filter === "limited") {
      return (
        card.analysis_type === "data_limited" ||
        card.evidence_confidence === "low"
      );
    }

    if (filter === "emerging") {
      return card.analysis_type === "emerging_lab";
    }

    return true;
  });

  return (
    <section className="space-y-6">
      <SectionTitle
        eyebrow="ProfessorCards"
        title="교수님 연구 경향 카드"
        description="LLM 요약 결과가 있으면 최근 키워드와 연구 경향을 우선 표시합니다."
      />

      <div className="flex flex-wrap gap-2">
        {filters.map((item) => (
          <button
            key={item.key}
            className={`rounded-full border px-3 py-1.5 text-xs font-semibold transition ${
              filter === item.key
                ? "border-gold bg-gold text-[#1E2420]"
                : "border-warm-gray/20 bg-dark-purple text-warm-gray hover:bg-dark-green"
            }`}
            onClick={() => onFilterChange(item.key)}
            type="button"
          >
            {item.label}
          </button>
        ))}
      </div>

      {!filtered.length ? (
        <EmptyState message="조건에 맞는 교수님 카드가 없습니다." />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {filtered.map((card) => {
            const selected = compareIds.includes(card.id);
            const compareDisabled = !selected && compareIds.length >= 3;

            const accepted = card.accepted_paper_count ?? card.accepted_count ?? 0;
            const needsReview =
              card.needs_review_paper_count ?? card.needs_review_count ?? 0;

            const displayKeywords =
              card.recent_keywords?.length
                ? card.recent_keywords
                : card.five_year_keywords?.length
                  ? card.five_year_keywords
                  : card.overall_keywords?.length
                    ? card.overall_keywords
                    : card.keywords ?? [];

            return (
              <article
                key={card.id}
                className="rounded-md border border-warm-gray/20 bg-dark-purple/80 p-5 shadow-soft"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-gold">
                      {card.university} · {card.department}
                    </p>

                    <h3 className="mt-2 text-xl font-bold text-white">
                      {card.name}
                    </h3>

                    <p className="mt-1 text-sm text-warm-gray">
                      {card.lab_name || "연구실명 확인 필요"}
                    </p>
                  </div>

                  <button
                    className={`rounded-md border p-2 transition ${
                      selected
                        ? "border-gold bg-gold text-[#1E2420]"
                        : "border-warm-gray/20 text-warm-gray hover:bg-dark-green"
                    } disabled:cursor-not-allowed disabled:opacity-40`}
                    onClick={() => onToggleCompare(card.id)}
                    disabled={compareDisabled}
                    title="연구 방향 비교에 추가"
                    type="button"
                  >
                    <GitCompare className="h-4 w-4" />
                  </button>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  <AnalysisTypeBadge type={card.analysis_type} />
                  <ConfidenceBadge confidence={card.evidence_confidence} />
                  {card.llm_used ? (
                    <Badge tone="purple">Gemini 요약</Badge>
                  ) : (
                    <Badge tone="muted">Fallback 요약</Badge>
                  )}
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  {displayKeywords.slice(0, 6).map((keyword) => (
                    <span
                      key={keyword}
                      className="rounded-full border border-green/20 bg-green/10 px-2 py-1 text-xs text-green"
                    >
                      {keyword}
                    </span>
                  ))}

                  {!displayKeywords.length ? (
                    <span className="text-xs text-warm-gray">
                      키워드 확인 필요
                    </span>
                  ) : null}
                </div>

                <p className="mt-4 rounded-md border border-warm-gray/15 bg-[#211C2B] p-3 text-sm leading-6 text-[#F0EDE8]">
                  <span className="font-semibold text-gold">연구 경향: </span>
                  {card.trend_summary ||
                    "공개 논문 데이터가 충분하지 않습니다. 연구실 소개와 교수소개 페이지를 중심으로 확인하세요."}
                </p>

                <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                  <div className="rounded-md bg-[#1B1724] p-3">
                    <p className="text-xs text-warm-gray">분석 사용 가능</p>
                    <p className="mt-1 text-lg font-bold text-white">
                      {accepted}
                    </p>
                  </div>

                  <div className="rounded-md bg-[#1B1724] p-3">
                    <p className="text-xs text-warm-gray">검증 필요</p>
                    <p className="mt-1 text-lg font-bold text-white">
                      {needsReview}
                    </p>
                  </div>
                </div>

                <button
                  className="mt-4 inline-flex items-center gap-2 rounded-md bg-gold px-4 py-2 text-sm font-bold text-[#1E2420] transition hover:scale-[1.02]"
                  onClick={() => onOpenDetail(card.id)}
                  type="button"
                >
                  자세히 보기 <ChevronRight className="h-4 w-4" />
                </button>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

export type { FilterKey };
