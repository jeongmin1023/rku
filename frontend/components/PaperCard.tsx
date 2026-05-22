import { ExternalLink } from "lucide-react";

import { MatchBadge, SourceBadge } from "@/components/Badge";
import type { AnalysisPaper, ProfessorPaper } from "@/lib/types";

type PaperCardProps = {
  paper: ProfessorPaper | AnalysisPaper;
  reason?: string | null;
  compact?: boolean;
};

export function PaperCard({ paper, reason, compact = false }: PaperCardProps) {
  const isLinkedPaper = "master_paper" in paper;
  const master = isLinkedPaper ? paper.master_paper : null;

  const title = isLinkedPaper
    ? paper.master_paper.display_title
    : paper.title ?? "제목 확인 필요";

  const venue = isLinkedPaper ? paper.master_paper.venue : paper.venue;
  const year = isLinkedPaper ? paper.master_paper.year : paper.year;
  const sourceList = isLinkedPaper
    ? paper.master_paper.source_list
    : paper.source_list ?? [];

  const citationSignals = isLinkedPaper
    ? paper.master_paper.citation_signals
    : paper.citation_signals ?? {};

  const status = paper.match_status;
  const authorRole = paper.author_role;
  const doi = master?.doi;
  const uci = master?.uci;
  const url = master?.url;

  const description =
    reason ??
    paper.paper_summary ??
    paper.why_read_this ??
    paper.category_reason ??
    ("reason" in paper ? paper.reason : undefined) ??
    null;

  return (
    <article className="rounded-md border border-warm-gray/20 bg-dark-purple/80 p-4 shadow-soft">
      <div className="space-y-2">
        <h4 className="text-sm font-bold leading-6 text-white">{title}</h4>

        <p className="text-xs text-warm-gray">
          {[year, venue].filter(Boolean).join(" · ") || "학술지/연도 확인 필요"}
        </p>

        <div className="flex flex-wrap gap-2">
          {status ? <MatchBadge status={status} /> : null}
          {authorRole ? (
            <span className="rounded-full border border-warm-gray/20 px-2 py-1 text-xs text-warm-gray">
              {authorRole}
            </span>
          ) : null}
          {paper.llm_used ? (
            <span className="rounded-full border border-purple/30 bg-purple/15 px-2 py-1 text-xs text-purple">
              AI 요약
            </span>
          ) : null}
        </div>

        {!compact && description ? (
          <p className="rounded-md border border-warm-gray/15 bg-[#211C2B] p-3 text-sm leading-6 text-[#F0EDE8]">
            {description}
          </p>
        ) : null}

        {!compact && paper.why_it_matters ? (
          <div className="rounded-md border border-green/20 bg-green/10 p-3">
            <p className="text-xs font-semibold text-green">연구실 탐색 관점</p>
            <p className="mt-1 text-sm leading-6 text-[#F0EDE8]">
              {paper.why_it_matters}
            </p>
          </div>
        ) : null}

        {!compact && paper.method_or_focus ? (
          <p className="text-xs text-warm-gray">
            방법/초점: {paper.method_or_focus}
          </p>
        ) : null}

        {paper.summary_limitations?.length ? (
          <div className="flex flex-wrap gap-2">
            {paper.summary_limitations.map((item) => (
              <span
                key={item}
                className="rounded-full border border-gold/20 bg-gold/10 px-2 py-1 text-xs text-gold"
              >
                {item}
              </span>
            ))}
          </div>
        ) : null}

        <div className="flex flex-wrap gap-2">
          {sourceList.map((source) => (
            <SourceBadge key={source} source={source} />
          ))}
          {!sourceList.length ? (
            <span className="text-xs text-warm-gray">출처 확인 필요</span>
          ) : null}
        </div>
      </div>

      {!compact ? (
        <div className="mt-4 grid gap-3 rounded-md border border-warm-gray/15 bg-[#1B1724] p-3 text-xs text-warm-gray md:grid-cols-2">
          <div>
            <p className="font-semibold text-[#F0EDE8]">DOI / UCI</p>
            <p className="mt-1">
              {[doi, uci].filter(Boolean).join(" · ") || "확인된 식별자 없음"}
            </p>
          </div>

          <div>
            <p className="font-semibold text-[#F0EDE8]">출처별 인용 신호</p>
            <p className="mt-1">
              {Object.entries(citationSignals).length
                ? Object.entries(citationSignals)
                    .map(
                      ([source, value]) =>
                        `${source.toUpperCase()} ${value ?? "확인 전"}`
                    )
                    .join(" / ")
                : "인용 신호 없음"}
            </p>
          </div>
        </div>
      ) : null}

      {isLinkedPaper && paper.warnings.length ? (
        <p className="mt-3 rounded-md border border-gold/20 bg-gold/10 p-2 text-xs text-gold">
          {paper.warnings.join(" ")}
        </p>
      ) : null}

      {url ? (
        <a
          className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-gold hover:underline"
          href={url}
          rel="noreferrer"
          target="_blank"
        >
          원문/메타데이터 링크 <ExternalLink className="h-3.5 w-3.5" />
        </a>
      ) : null}
    </article>
  );
}
