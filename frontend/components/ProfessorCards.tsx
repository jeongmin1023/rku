import { BookOpen, ChevronRight, GitCompare, SearchCheck } from "lucide-react";

import { AnalysisTypeBadge, ConfidenceBadge } from "@/components/Badge";
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
    if (filter === "recent") return (card.trend_summary ?? "").includes("최근") || (card.accepted_count ?? 0) > 0;
    if (filter === "sufficient") return (card.accepted_count ?? 0) >= 3 || card.evidence_confidence === "high";
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
              className={`focus-ring rounded-full border px-3 py-1.5 text-sm font-semibold ${
                filter === item.key ? "border-navy-900 bg-navy-900 text-white" : "border-line bg-white text-slate-700 hover:bg-mist"
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
        <div className="grid gap-4 lg:grid-cols-3">
          {filtered.map((card) => {
            const selected = compareIds.includes(card.id);
            const compareDisabled = !selected && compareIds.length >= 3;
            return (
              <article key={card.id} className="flex min-h-full flex-col rounded-md border border-line bg-white p-5 shadow-soft">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold text-navy-900">{card.name}</h3>
                    <p className="mt-1 text-sm text-slate-600">{card.lab_name || "연구실명 확인 필요"}</p>
                  </div>
                  <button
                    className={`focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border ${
                      selected ? "border-bluepoint bg-bluepoint text-white" : "border-line bg-white text-slate-600 hover:bg-mist"
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
                    <span key={keyword} className="rounded-full bg-mist px-2.5 py-1 text-xs font-semibold text-slate-700">
                      {keyword}
                    </span>
                  ))}
                </div>

                <p className="mt-4 flex-1 text-sm leading-6 text-slate-700">{card.trend_summary || "논문 수집 후 최근 연구 경향을 확인할 수 있습니다."}</p>

                <dl className="mt-5 grid grid-cols-2 gap-x-4 gap-y-2 border-t border-line pt-4 text-sm">
                  <div>
                    <dt className="flex items-center gap-1.5 text-xs font-semibold text-slate-500">
                      <BookOpen className="h-3.5 w-3.5" aria-hidden />
                      accepted 논문
                    </dt>
                    <dd className="mt-1 font-semibold text-navy-900">{card.accepted_count ?? 0}</dd>
                  </div>
                  <div>
                    <dt className="flex items-center gap-1.5 text-xs font-semibold text-slate-500">
                      <SearchCheck className="h-3.5 w-3.5" aria-hidden />
                      검증 필요
                    </dt>
                    <dd className="mt-1 font-semibold text-navy-900">{card.needs_review_count ?? 0}</dd>
                  </div>
                </dl>

                <button
                  className="focus-ring mt-5 inline-flex items-center justify-center gap-2 rounded-md bg-navy-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-navy-800"
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
