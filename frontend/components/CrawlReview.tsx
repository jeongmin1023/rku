import { ExternalLink, FileSearch, Trash2 } from "lucide-react";

import { EmptyState, SectionTitle } from "@/components/StateBlocks";
import type { ConfirmProfessor, CrawlResponse } from "@/lib/types";

type CrawlReviewProps = {
  crawl: CrawlResponse;
  draft: ConfirmProfessor[];
  onDraftChange: (next: ConfirmProfessor[]) => void;
  onHarvest: () => void;
  loading: boolean;
};

export function CrawlReview({ crawl, draft, onDraftChange, onHarvest, loading }: CrawlReviewProps) {
  function update(index: number, patch: Partial<ConfirmProfessor>) {
    onDraftChange(draft.map((item, current) => (current === index ? { ...item, ...patch } : item)));
  }

  const included = draft.filter((item) => !item.excluded);

  return (
    <section className="space-y-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <SectionTitle
          eyebrow="Crawl Review"
          title="크롤링 결과 확인"
          description="학과 페이지 구조가 대학마다 다르기 때문에, 논문 수집 전에 교수님 이름과 연구분야를 가볍게 확인하세요."
        />
        <button
          className="focus-ring inline-flex items-center justify-center gap-2 rounded-md bg-navy-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-navy-800 disabled:cursor-not-allowed disabled:bg-slate-400"
          onClick={onHarvest}
          disabled={loading || included.length === 0}
          type="button"
        >
          <FileSearch className="h-4 w-4" aria-hidden />
          논문 수집 시작
        </button>
      </div>

      {crawl.warnings.length ? (
        <div className="rounded-md border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-900">
          {crawl.warnings.join(" ")}
        </div>
      ) : null}

      {!draft.length ? (
        <EmptyState message="교수님 후보가 없습니다. URL을 확인하거나 샘플 모드로 화면을 확인하세요." />
      ) : (
        <div className="overflow-hidden rounded-md border border-line bg-white shadow-soft">
          <div className="grid grid-cols-[minmax(160px,1.1fr)_minmax(120px,.6fr)_minmax(180px,1fr)_minmax(240px,1.5fr)_120px] gap-0 border-b border-line bg-mist px-4 py-3 text-xs font-semibold text-slate-600 max-xl:hidden">
            <span>교수명</span>
            <span>직위</span>
            <span>이메일</span>
            <span>연구분야</span>
            <span>확인</span>
          </div>

          <div className="divide-y divide-line">
            {draft.map((professor, index) => (
              <div key={`${professor.name}-${index}`} className={`grid gap-3 p-4 xl:grid-cols-[minmax(160px,1.1fr)_minmax(120px,.6fr)_minmax(180px,1fr)_minmax(240px,1.5fr)_120px] ${professor.excluded ? "bg-slate-50 opacity-65" : "bg-white"}`}>
                <label className="space-y-1">
                  <span className="text-xs font-semibold text-slate-500 xl:hidden">교수명</span>
                  <input
                    className="focus-ring w-full rounded-md border border-line bg-white px-3 py-2 text-sm"
                    value={professor.name}
                    onChange={(event) => update(index, { name: event.target.value })}
                  />
                  <span className="block text-xs text-slate-500">추출 신뢰도 {Math.round(professor.extraction_confidence * 100)}%</span>
                </label>

                <label className="space-y-1">
                  <span className="text-xs font-semibold text-slate-500 xl:hidden">직위</span>
                  <input
                    className="focus-ring w-full rounded-md border border-line bg-white px-3 py-2 text-sm"
                    value={professor.title ?? ""}
                    onChange={(event) => update(index, { title: event.target.value })}
                    placeholder="교수"
                  />
                </label>

                <div className="space-y-1">
                  <span className="text-xs font-semibold text-slate-500 xl:hidden">이메일</span>
                  <p className="break-words text-sm text-slate-700">{professor.email || "이메일 확인 필요"}</p>
                  <div className="flex flex-wrap gap-3 text-xs font-semibold text-bluepoint">
                    {professor.profile_url ? (
                      <a className="inline-flex items-center gap-1" href={professor.profile_url} target="_blank" rel="noreferrer">
                        교수소개 <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    ) : null}
                    {professor.lab_url ? (
                      <a className="inline-flex items-center gap-1" href={professor.lab_url} target="_blank" rel="noreferrer">
                        연구실 <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    ) : null}
                  </div>
                </div>

                <label className="space-y-1">
                  <span className="text-xs font-semibold text-slate-500 xl:hidden">연구분야</span>
                  <textarea
                    className="focus-ring min-h-20 w-full resize-y rounded-md border border-line bg-white px-3 py-2 text-sm leading-5"
                    value={professor.official_keywords ?? ""}
                    onChange={(event) => update(index, { official_keywords: event.target.value })}
                    placeholder="연구분야 확인 필요"
                  />
                </label>

                <div className="flex items-start justify-between gap-2 xl:justify-end">
                  <label className="inline-flex items-center gap-2 text-sm font-medium text-slate-700">
                    <input
                      type="checkbox"
                      className="h-4 w-4 rounded border-line text-bluepoint"
                      checked={professor.excluded}
                      onChange={(event) => update(index, { excluded: event.target.checked })}
                    />
                    제외
                  </label>
                  <button
                    className="focus-ring inline-flex items-center gap-1 rounded-md border border-line px-2 py-1.5 text-xs font-semibold text-slate-600 hover:bg-mist"
                    type="button"
                    onClick={() => update(index, { excluded: true })}
                  >
                    <Trash2 className="h-3.5 w-3.5" aria-hidden />
                    제외
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
