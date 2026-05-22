import { ChevronRight, GitCompare } from "lucide-react";

import { AnalysisTypeBadge, Badge, ConfidenceBadge } from "@/components/Badge";
import { EmptyState, SectionTitle } from "@/components/StateBlocks";
import type { ProfessorCard } from "@/lib/types";

type FilterKey = "all" | "interest" | "recent" | "sufficient" | "limited" | "emerging";

const filters: Array<{ key: FilterKey; label: string }> = [
  { key: "all", label: "전체" },
  { key: "interest", label: "내 관심 주제와 가까움" },
  { key: "recent", label: "최근 논문 있음" },
  { key: "sufficient", label: "논문 데이터 충분" },
  { key: "limited", label: "공개 데이터 제한" },
  { key: "emerging", label: "Emerging Lab" }
];

export function ProfessorCards({
  cards,
  filter,
  onFilterChange,
  onOpenDetail,
  compareIds,
  onToggleCompare,
  userInterest
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
      const haystack = [...card.keywords, card.trend_summary ?? "", card.official_keywords ?? ""].join(" ").toLowerCase();
      return interestTokens.some((token) => haystack.includes(token));
    }
    if (filter === "recent") return (card.recent_keywords?.length ?? 0) > 0 || (card.accepted_paper_count ?? card.accepted_count ?? 0) > 0;
    if (filter === "sufficient") return (card.accepted_paper_count ?? card.accepted_count ?? 0) >= 3 || card.evidence_confidence === "high";
    if (filter === "limited") return card.analysis_type === "data_limited" || card.evidence_confidence === "low";
    if (filter === "emerging") return card.analysis_type === "emerging_lab";
    return true;
  });

  return (
    <section className="space-y-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <SectionTitle
          eyebrow="Professor Cards"
          title="교수님 연구 방향 카드"
          description="카드는 우열 비교가 아니라 공개 근거와 관심 주제의 연결성을 확인하기 위한 탐색 단위입니다."
        />
        <div className="flex flex-wrap gap-2">
          {filters.map((item) => (
            <button
              key={item.key}
              className={`focus-ring rounded-md border px-3 py-1.5 text-sm font-semibold transition duration-150 ${
                filter === item.key ? "border-gold bg-gold text-[#1E2420]" : "border-warm-gray/20 bg-dark-purple text-warm-gray hover:bg-dark-green hover:text-white"
              }`}
              onClick={() => onFilterChange(item.key)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {!filtered.length ? (
        <EmptyState message="조건에 맞는 교수님 카드가 없습니다. 필터를 바꾸거나 관심 주제를 더 넓게 입력해보세요." />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((card, index) => {
            const selected = compareIds.includes(card.id);
            const compareDisabled = !selected && compareIds.length >= 3;
            const accepted = card.accepted_paper_count ?? card.accepted_count ?? 0;
            const needsReview = card.needs_review_paper_count ?? card.needs_review_count ?? 0;
            return (
              <article
                key={card.id}
                className="card-enter flex min-h-full flex-col rounded-md border border-warm-gray/20 bg-dark-purple p-5 shadow-soft transition duration-150 hover:-translate-y-1 hover:bg-dark-green"
                style={{ animationDelay: `${index * 70}ms` }}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold text-white">{card.name}</h3>
                    <p className="mt-1 text-sm text-warm-gray">{card.lab_name || "연구실명 확인 필요"}</p>
                  </div>
                  <button
                    className={`focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border ${
                      selected ? "border-gold bg-gold text-[#1E2420]" : "border-warm-gray/20 bg-[#2E2838] text-warm-gray hover:bg-dark-green hover:text-white"
                    } disabled:cursor-not-allowed disabled:opacity-45`}
                    type="button"
                    onClick={() => onToggleCompare(card.id)}
                    disabled={compareDisabled}
                    title="연구 방향 비교에 추가"
                  >
                    <GitCompare className="h-4 w-4" aria-hidden />
                  </button>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  <AnalysisTypeBadge type={card.analysis_type} />
                  <ConfidenceBadge confidence={card.evidence_confidence} />
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  {card.keywords.slice(0, 5).map((keyword) => (
                    <span key={keyword} className="rounded-full border border-purple/30 bg-purple/15 px-2.5 py-1 text-xs font-semibold text-purple">
                      {keyword}
                    </span>
                  ))}
                </div>

                <p className="mt-4 text-sm leading-6 text-[#F0EDE8]">
                  <span className="font-semibold text-gold">연구 경향: </span>
                  {card.trend_summary || "공개 논문 데이터가 충분하지 않습니다. 연구실 소개와 교수소개 페이지를 중심으로 확인하세요."}
                </p>

                <div className="mt-4 flex flex-wrap gap-2">
                  {Object.entries(card.source_coverage ?? {}).map(([source, count]) => (
                    <Badge key={source} tone="muted">
                      {source} {count}
                    </Badge>
                  ))}
                </div>

                <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                  <div className="rounded-md bg-[#2E2838] p-3">
                    <p className="text-xs text-warm-gray">분석 사용 가능</p>
                    <p className="mt-1 text-lg font-bold text-green">{accepted}</p>
                  </div>
                  <div className="rounded-md bg-[#2E2838] p-3">
                    <p className="text-xs text-warm-gray">핏 레벨</p>
                    <p className="mt-1 text-lg font-bold text-gold">{needsReview ? "Medium" : "Ready"}</p>
                  </div>
                </div>

                <button
                  className="focus-ring mt-5 inline-flex items-center justify-center gap-2 rounded-md bg-gold px-4 py-2.5 text-sm font-bold text-[#1E2420] transition duration-150 hover:scale-[1.02] hover:bg-[#C89A5E]"
                  type="button"
                  onClick={() => onOpenDetail(card.id)}
                >
                  자세히 보기
                  <ChevronRight className="h-4 w-4" aria-hidden />
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
