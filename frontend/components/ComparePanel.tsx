import { X } from "lucide-react";

import { AnalysisTypeBadge, ConfidenceBadge } from "@/components/Badge";
import { EmptyState, SectionTitle } from "@/components/StateBlocks";
import type { FitResult, ProfessorDetail } from "@/lib/types";

export function ComparePanel({
  details,
  fitByProfessor,
  onRemove
}: {
  details: ProfessorDetail[];
  fitByProfessor: Record<number, FitResult | undefined>;
  onRemove: (id: number) => void;
}) {
  return (
    <section className="space-y-5">
      <SectionTitle
        eyebrow="Compare"
        title="연구 방향 비교"
        description="이 비교는 우열 비교가 아니라 사용자의 관심 주제와 각 연구실의 방향성을 나란히 확인하기 위한 것입니다."
      />

      {!details.length ? (
        <EmptyState message="교수님 카드의 비교 아이콘을 눌러 최대 3명까지 연구 방향을 나란히 확인할 수 있습니다." />
      ) : (
        <div className="grid gap-4 lg:grid-cols-3">
          {details.map((detail) => {
            const fit = fitByProfessor[detail.id];
            return (
              <article key={detail.id} className="rounded-md border border-line bg-white p-5 shadow-soft">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold text-navy-900">{detail.name}</h3>
                    <p className="mt-1 text-sm text-slate-600">{detail.lab_name || "연구실명 확인 필요"}</p>
                  </div>
                  <button
                    className="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-line text-slate-600 hover:bg-mist"
                    type="button"
                    onClick={() => onRemove(detail.id)}
                    title="비교에서 제거"
                  >
                    <X className="h-4 w-4" aria-hidden />
                  </button>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  <AnalysisTypeBadge type={detail.analysis_type} />
                  <ConfidenceBadge confidence={detail.analysis.evidence_confidence} />
                </div>

                <CompareBlock title="연구 키워드" items={detail.analysis.five_year_keywords.slice(0, 5)} />
                <CompareText title="최근 연구 방향" text={detail.analysis.trend_summary} />
                <CompareText
                  title="대표 논문"
                  text={detail.analysis.representative_papers[0]?.title || "공개 논문 데이터가 충분하지 않습니다."}
                />
                <CompareText
                  title="최근 논문"
                  text={detail.analysis.recent_papers[0]?.title || "최근 논문 확인 필요"}
                />
                <CompareText
                  title="내 관심 주제와 맞는 부분"
                  text={fit?.interpretation || "관심 주제 분석 후 연결 근거가 표시됩니다."}
                />
                <CompareBlock title="확인 필요한 부분" items={fit?.check_points ?? detail.analysis.warnings} />
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

function CompareBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="mt-5 border-t border-line pt-4">
      <h4 className="text-xs font-semibold uppercase tracking-[0.08em] text-slate-500">{title}</h4>
      {items.length ? (
        <div className="mt-2 flex flex-wrap gap-2">
          {items.slice(0, 5).map((item) => (
            <span key={item} className="rounded-full bg-mist px-2.5 py-1 text-xs font-semibold text-slate-700">
              {item}
            </span>
          ))}
        </div>
      ) : (
        <p className="mt-2 text-sm text-slate-500">확인 필요</p>
      )}
    </div>
  );
}

function CompareText({ title, text }: { title: string; text: string }) {
  return (
    <div className="mt-5 border-t border-line pt-4">
      <h4 className="text-xs font-semibold uppercase tracking-[0.08em] text-slate-500">{title}</h4>
      <p className="mt-2 text-sm leading-6 text-slate-700">{text}</p>
    </div>
  );
}
