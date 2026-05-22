import { ExternalLink } from "lucide-react";

import { MatchBadge, SourceBadge } from "@/components/Badge";
import type { AnalysisPaper, ProfessorPaper } from "@/lib/types";

type PaperCardProps = {
  paper: ProfessorPaper | AnalysisPaper;
  reason?: string;
  compact?: boolean;
};

export function PaperCard({ paper, reason, compact = false }: PaperCardProps) {
  const isLinkedPaper = "master_paper" in paper;
  const master = isLinkedPaper ? paper.master_paper : null;
  const title = isLinkedPaper ? paper.master_paper.display_title : (paper.title ?? "제목 확인 필요");
  const venue = isLinkedPaper ? paper.master_paper.venue : paper.venue;
  const year = isLinkedPaper ? paper.master_paper.year : paper.year;
  const sourceList = master?.source_list ?? [];
  const citationSignals = isLinkedPaper ? paper.master_paper.citation_signals : (paper.citation_signals ?? {});
  const status = paper.match_status;
  const authorRole = isLinkedPaper ? paper.author_role : undefined;
  const doi = master?.doi;
  const uci = master?.uci;
  const url = master?.url;
  const description = reason ?? (isLinkedPaper ? undefined : paper.reason);

  return (
    <article className="rounded-md border border-line bg-white p-4 shadow-soft">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h4 className="text-base font-semibold leading-6 text-navy-900">{title}</h4>
          <p className="mt-1 text-sm text-slate-600">
            {[year, venue].filter(Boolean).join(" · ") || "학술지/연도 확인 필요"}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {status ? <MatchBadge status={status} /> : null}
          {authorRole ? <span className="rounded-full border border-line bg-mist px-2.5 py-1 text-xs font-semibold text-slate-700">{authorRole}</span> : null}
        </div>
      </div>

      {!compact && description ? <p className="mt-3 text-sm leading-6 text-slate-700">{description}</p> : null}

      <div className="mt-4 flex flex-wrap gap-2">
        {sourceList.map((source) => (
          <SourceBadge key={source} source={source} />
        ))}
        {!sourceList.length && <span className="text-xs text-slate-500">출처 확인 필요</span>}
      </div>

      {!compact ? (
        <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-xs font-semibold text-slate-500">DOI / UCI</dt>
            <dd className="mt-1 break-words text-slate-700">{[doi, uci].filter(Boolean).join(" · ") || "확인된 식별자 없음"}</dd>
          </div>
          <div>
            <dt className="text-xs font-semibold text-slate-500">출처별 인용 신호</dt>
            <dd className="mt-1 text-slate-700">
              {Object.entries(citationSignals).length
                ? Object.entries(citationSignals)
                    .map(([source, value]) => `${source.toUpperCase()} 인용 신호 ${value ?? "확인 전"}`)
                    .join(" / ")
                : "인용 신호 없음"}
            </dd>
          </div>
        </dl>
      ) : null}

      {isLinkedPaper && paper.warnings.length ? (
        <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm leading-6 text-amber-900">
          {paper.warnings.join(" ")}
        </div>
      ) : null}

      {url ? (
        <a className="focus-ring mt-4 inline-flex items-center gap-2 rounded-md text-sm font-semibold text-bluepoint hover:text-navy-800" href={url} target="_blank" rel="noreferrer">
          원문/식별자 링크
          <ExternalLink className="h-4 w-4" aria-hidden />
        </a>
      ) : null}
    </article>
  );
}
