"use client";

import {
  CheckCircle2,
  Mail,
  MessageSquare,
  NotebookText,
  Search,
} from "lucide-react";
import { useMemo, useState, type ReactNode } from "react";

import { AnalysisTypeBadge, ConfidenceBadge } from "@/components/Badge";
import { PaperCard } from "@/components/PaperCard";
import { EmptyState, SectionTitle } from "@/components/StateBlocks";
import type {
  AnalysisPaper,
  ContactCard,
  FitResult,
  ProfessorDetail as ProfessorDetailType,
  ProfessorPaper,
} from "@/lib/types";

type TabKey = "summary" | "papers" | "fit" | "contact";

const tabs: Array<{ key: TabKey; label: string }> = [
  { key: "summary", label: "연구 요약" },
  { key: "papers", label: "논문" },
  { key: "fit", label: "내 관심 주제와 비교" },
  { key: "contact", label: "컨택 준비" },
];

export function ProfessorDetail({
  detail,
  initialInterest,
  fit,
  contact,
  loadingFit,
  loadingContact,
  error,
  onAnalyzeFit,
  onBuildContact,
}: {
  detail: ProfessorDetailType;
  initialInterest: string;
  fit?: FitResult | null;
  contact?: ContactCard | null;
  loadingFit: boolean;
  loadingContact: boolean;
  error?: string | null;
  onAnalyzeFit: (interest: string) => void;
  onBuildContact: (interest: string) => void;
}) {
  const [activeTab, setActiveTab] = useState<TabKey>("summary");
  const [interest, setInterest] = useState(initialInterest);

  const papersById = useMemo(() => {
    const map = new Map<number, ProfessorPaper>();
    detail.papers.forEach((paper) => map.set(paper.master_paper.id, paper));
    return map;
  }, [detail.papers]);

  const accepted = detail.papers.filter((paper) => paper.match_status === "accepted");
  const needsReview = detail.papers.filter((paper) => paper.match_status === "needs_review");
  const weak = detail.papers.filter((paper) => paper.match_status === "weak_candidate");

  return (
    <section className="space-y-6">
      <div className="rounded-md border border-warm-gray/20 bg-dark-purple/80 p-5 shadow-soft">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-gold">
          {detail.department_info.university} · {detail.department_info.department}
        </p>

        <h2 className="mt-2 text-2xl font-bold text-white">{detail.name}</h2>

        <p className="mt-2 text-sm text-warm-gray">
          {detail.lab_name || "연구실명 확인 필요"} · {detail.email || "이메일 확인 필요"}
        </p>

        <div className="mt-4 flex flex-wrap gap-2">
          <AnalysisTypeBadge type={detail.analysis_type} />
          <ConfidenceBadge confidence={detail.analysis.evidence_confidence} />
          <span className="rounded-full border border-warm-gray/20 px-2 py-1 text-xs text-warm-gray">
            {detail.analysis.llm_used ? "Gemini 요약" : "Fallback 요약"}
          </span>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            className={`rounded-full border px-3 py-1.5 text-xs font-semibold transition ${
              activeTab === tab.key
                ? "border-gold bg-gold text-[#1E2420]"
                : "border-warm-gray/20 bg-dark-purple text-warm-gray hover:bg-dark-green"
            }`}
            onClick={() => setActiveTab(tab.key)}
            type="button"
          >
            {tab.label}
          </button>
        ))}
      </div>

      {error ? (
        <div className="rounded-md border border-gold/20 bg-gold/10 p-3 text-sm text-gold">
          {error}
        </div>
      ) : null}

      {activeTab === "summary" ? (
        <SummaryTab
          detail={detail}
          acceptedCount={accepted.length}
          needsReviewCount={needsReview.length}
          weakCount={weak.length}
        />
      ) : null}

      {activeTab === "papers" ? (
        <PapersTab detail={detail} papersById={papersById} fit={fit} />
      ) : null}

      {activeTab === "fit" ? (
        <FitTab
          interest={interest}
          onInterestChange={setInterest}
          fit={fit}
          loading={loadingFit}
          onAnalyze={() => onAnalyzeFit(interest)}
        />
      ) : null}

      {activeTab === "contact" ? (
        <ContactTab
          interest={interest}
          onInterestChange={setInterest}
          contact={contact}
          loading={loadingContact}
          onBuild={() => onBuildContact(interest)}
        />
      ) : null}
    </section>
  );
}

function SummaryTab({
  detail,
  acceptedCount,
  needsReviewCount,
  weakCount,
}: {
  detail: ProfessorDetailType;
  acceptedCount: number;
  needsReviewCount: number;
  weakCount: number;
}) {
  const timelineEntries = Object.entries(detail.analysis.timeline ?? {});

  return (
    <div className="space-y-5">
      <div className="rounded-md border border-warm-gray/20 bg-dark-purple/80 p-5 shadow-soft">
        <SectionTitle
          eyebrow="Research Trend"
          title="연구 경향 요약"
          description="LLM 결과가 있으면 Gemini 요약을 우선 표시합니다."
        />

        <p className="mt-4 rounded-md border border-warm-gray/15 bg-[#211C2B] p-4 text-sm leading-6 text-[#F0EDE8]">
          {detail.analysis.trend_summary || "연구 경향 요약을 확인할 수 없습니다."}
        </p>

        {detail.analysis.detailed_trend_summary ? (
          <p className="mt-4 text-sm leading-6 text-warm-gray">
            {detail.analysis.detailed_trend_summary}
          </p>
        ) : null}

        {detail.analysis.recent_shift ? (
          <div className="mt-4 rounded-md border border-purple/20 bg-purple/10 p-3">
            <p className="text-xs font-semibold text-purple">최근 변화</p>
            <p className="mt-1 text-sm leading-6 text-[#F0EDE8]">
              {detail.analysis.recent_shift}
            </p>
          </div>
        ) : null}

        <div className="mt-4 grid gap-3 md:grid-cols-3">
          <KeywordBlock title="전체 키워드" keywords={detail.analysis.overall_keywords ?? []} />
          <KeywordBlock title="최근 키워드" keywords={detail.analysis.recent_keywords ?? []} />
          <KeywordBlock title="최근 5년 키워드" keywords={detail.analysis.five_year_keywords ?? []} />
        </div>

        {detail.analysis.main_research_axis?.length ? (
          <CheckList
            title="주요 연구축"
            icon={<NotebookText className="h-4 w-4" />}
            items={detail.analysis.main_research_axis}
          />
        ) : null}
      </div>

      <div className="rounded-md border border-warm-gray/20 bg-dark-purple/80 p-5 shadow-soft">
        <h3 className="text-base font-semibold text-white">연구 흐름 타임라인</h3>
        {timelineEntries.length ? (
          <div className="mt-4 space-y-3">
            {timelineEntries.map(([year, keywords]) => (
              <div key={year} className="rounded-md border border-warm-gray/15 bg-[#211C2B] p-3">
                <p className="text-sm font-bold text-gold">{year}</p>
                <p className="mt-1 text-sm text-warm-gray">{keywords.join(", ")}</p>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState message="연도별 연구 흐름 데이터가 아직 부족합니다." />
        )}
      </div>

      <div className="rounded-md border border-warm-gray/20 bg-dark-purple/80 p-5 shadow-soft">
        <h3 className="text-base font-semibold text-white">근거 상태</h3>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          <Row label="분석 사용 가능" value={acceptedCount} />
          <Row label="검증 필요" value={needsReviewCount} />
          <Row label="낮은 신뢰도 후보" value={weakCount} />
        </div>
        <p className="mt-4 text-xs text-warm-gray">
          LLM 사용: {detail.analysis.llm_used ? "Gemini 요약" : "Fallback 요약"}
          {detail.analysis.llm_provider ? ` · ${detail.analysis.llm_provider}` : ""}
        </p>
        {detail.analysis.warnings.length ? (
          <div className="mt-4 space-y-2">
            {detail.analysis.warnings.map((warning) => (
              <p key={warning} className="rounded-md border border-gold/20 bg-gold/10 p-2 text-xs text-gold">
                {warning}
              </p>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}

function PapersTab({ detail, papersById, fit }: { detail: ProfessorDetailType; papersById: Map<number, ProfessorPaper>; fit?: FitResult | null }) {
  const representative = detail.analysis.representative_papers ?? [];
  const recent = detail.analysis.recent_important_papers?.length
    ? detail.analysis.recent_important_papers
    : detail.analysis.recent_papers ?? [];
  const interestRelated = fit?.related_papers ?? detail.analysis.interest_related_papers ?? [];
  const supporting = detail.analysis.supporting_papers ?? [];

  return (
    <div className="space-y-6">
      <PaperSection title="대표 논문" description="교수님의 기존 연구축을 이해하는 데 도움이 되는 논문입니다." papers={representative} papersById={papersById} />
      <PaperSection title="최근 연구 논문" description="최근 3~5년 연구 방향을 파악하기 좋은 논문입니다." papers={recent} papersById={papersById} />
      <PaperSection title="내 관심주제 관련 논문" description="입력한 관심 연구주제와 연결해서 읽어볼 수 있는 논문입니다." papers={interestRelated} papersById={papersById} empty="관심주제 분석을 실행하면 관련 논문이 표시됩니다." />
      <PaperSection title="보조 후보 논문" description="검증 필요 또는 낮은 신뢰도 후보 중 추가 확인용으로 볼 수 있는 논문입니다." papers={supporting} papersById={papersById} />
    </div>
  );
}

function PaperSection({ title, description, papers, papersById, empty = "공개 논문 데이터가 충분하지 않습니다. 연구실 소개와 교수소개 페이지를 중심으로 확인하세요." }: { title: string; description: string; papers: AnalysisPaper[]; papersById: Map<number, ProfessorPaper>; empty?: string }) {
  return (
    <section className="space-y-3">
      <SectionTitle title={title} description={description} />
      {papers.length ? (
        <div className="grid gap-3">
          {papers.map((paper, index) => {
            const linked = typeof paper.id === "number" ? papersById.get(paper.id) : undefined;
            const reason = paper.paper_summary ?? paper.why_read_this ?? paper.category_reason ?? paper.reason ?? null;
            return linked ? (
              <PaperCard
                key={`${title}-${paper.id ?? index}`}
                paper={{
                  ...linked,
                  paper_summary: paper.paper_summary ?? linked.paper_summary,
                  why_read_this: paper.why_read_this ?? linked.why_read_this,
                  category_reason: paper.category_reason ?? linked.category_reason,
                  why_it_matters: paper.why_it_matters ?? linked.why_it_matters,
                  method_or_focus: paper.method_or_focus ?? linked.method_or_focus,
                  summary_limitations: paper.summary_limitations ?? linked.summary_limitations,
                  llm_used: paper.llm_used ?? linked.llm_used,
                  llm_provider: paper.llm_provider ?? linked.llm_provider,
                }}
                reason={reason}
              />
            ) : (
              <PaperCard key={`${title}-${paper.id ?? paper.title ?? index}`} paper={paper} reason={reason} />
            );
          })}
        </div>
      ) : (
        <EmptyState message={empty} />
      )}
    </section>
  );
}

function FitTab({ interest, onInterestChange, fit, loading, onAnalyze }: { interest: string; onInterestChange: (value: string) => void; fit?: FitResult | null; loading: boolean; onAnalyze: () => void }) {
  return (
    <div className="space-y-5">
      <div className="rounded-md border border-warm-gray/20 bg-dark-purple/80 p-5 shadow-soft">
        <label className="block text-sm font-semibold text-white">
          관심 연구주제
          <input className="mt-2 w-full rounded-md border border-warm-gray/20 bg-[#211C2B] px-3 py-2 text-sm text-white outline-none focus:border-gold" value={interest} onChange={(event) => onInterestChange(event.target.value)} placeholder="예: LLM 기반 교육 서비스" />
        </label>
        <button className="mt-4 inline-flex items-center gap-2 rounded-md bg-gold px-4 py-2 text-sm font-bold text-[#1E2420] disabled:opacity-60" onClick={onAnalyze} disabled={loading} type="button">
          <Search className="h-4 w-4" />
          {loading ? "분석 중" : "연구핏 분석하기"}
        </button>
      </div>
      {fit ? (
        <div className="rounded-md border border-warm-gray/20 bg-dark-purple/80 p-5 shadow-soft">
          <h3 className="text-lg font-bold text-white">{fit.fit_level}</h3>
          <p className="mt-3 text-sm leading-6 text-warm-gray">{fit.interpretation}</p>
          <CheckList title="연결 키워드" icon={<CheckCircle2 className="h-4 w-4" />} items={fit.matched_keywords.map((keyword) => `${keyword} 관련 공개 연구 신호가 감지됩니다.`)} />
          <CheckList title="컨택 전 확인할 점" icon={<MessageSquare className="h-4 w-4" />} items={fit.check_points} />
        </div>
      ) : (
        <EmptyState message="관심 주제를 입력하고 연구핏 분석을 실행해보세요." />
      )}
    </div>
  );
}

function ContactTab({ interest, onInterestChange, contact, loading, onBuild }: { interest: string; onInterestChange: (value: string) => void; contact?: ContactCard | null; loading: boolean; onBuild: () => void }) {
  return (
    <div className="space-y-5">
      <div className="rounded-md border border-warm-gray/20 bg-dark-purple/80 p-5 shadow-soft">
        <label className="block text-sm font-semibold text-white">
          컨택에서 묻고 싶은 관심 주제
          <input className="mt-2 w-full rounded-md border border-warm-gray/20 bg-[#211C2B] px-3 py-2 text-sm text-white outline-none focus:border-gold" value={interest} onChange={(event) => onInterestChange(event.target.value)} placeholder="예: LLM 기반 교육 서비스" />
        </label>
        <button className="mt-4 inline-flex items-center gap-2 rounded-md bg-gold px-4 py-2 text-sm font-bold text-[#1E2420] disabled:opacity-60" onClick={onBuild} disabled={loading} type="button">
          <Mail className="h-4 w-4" />
          {loading ? "생성 중" : "컨택 카드 보기"}
        </button>
      </div>
      {contact ? (
        <div className="space-y-5">
          <section className="rounded-md border border-warm-gray/20 bg-dark-purple/80 p-5 shadow-soft">
            <h3 className="text-lg font-bold text-white">컨택 전 읽을 논문</h3>
            <div className="mt-4 grid gap-3">
              {contact.reading_list.map((paper, index) => (
                <article key={`${paper.title ?? "paper"}-${index}`} className="rounded-md border border-warm-gray/15 bg-[#211C2B] p-3">
                  <p className="text-xs font-semibold text-gold">{paper.category}</p>
                  <h4 className="mt-1 text-sm font-bold text-white">{paper.title || "자료 확인 필요"}</h4>
                  <p className="mt-2 text-sm leading-6 text-warm-gray">{paper.paper_summary ?? paper.why_read_this ?? paper.category_reason ?? paper.why_read}</p>
                </article>
              ))}
            </div>
          </section>
          <CheckList title="교수님께 물어볼 질문" icon={<MessageSquare className="h-4 w-4" />} items={contact.questions} />
          <CheckList title="메일에 넣을 포인트" icon={<Mail className="h-4 w-4" />} items={contact.email_points} />
          <CheckList title="확인할 점" icon={<CheckCircle2 className="h-4 w-4" />} items={contact.check_points} />
        </div>
      ) : (
        <EmptyState message="관심 주제를 입력하고 컨택 카드를 생성해보세요." />
      )}
    </div>
  );
}

function KeywordBlock({ title, keywords }: { title: string; keywords: string[] }) {
  return (
    <div className="rounded-md border border-warm-gray/15 bg-[#211C2B] p-3">
      <h3 className="text-sm font-semibold text-white">{title}</h3>
      {keywords.length ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {keywords.map((keyword) => (
            <span key={keyword} className="rounded-full border border-green/20 bg-green/10 px-2 py-1 text-xs text-green">
              {keyword}
            </span>
          ))}
        </div>
      ) : (
        <p className="mt-2 text-xs text-warm-gray">키워드 확인 필요</p>
      )}
    </div>
  );
}

function CheckList({ title, icon, items }: { title: string; icon: ReactNode; items: string[] }) {
  return (
    <section className="rounded-md border border-warm-gray/20 bg-dark-purple/80 p-5 shadow-soft">
      <h3 className="flex items-center gap-2 text-base font-semibold text-white">
        {icon} {title}
      </h3>
      {items.length ? (
        <ul className="mt-3 space-y-2 text-sm leading-6 text-warm-gray">
          {items.map((item) => <li key={item}>• {item}</li>)}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-warm-gray">확인할 항목이 없습니다.</p>
      )}
    </section>
  );
}

function Row({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-warm-gray/15 bg-[#211C2B] p-3">
      <p className="text-xs text-warm-gray">{label}</p>
      <p className="mt-1 text-lg font-bold text-white">{value}</p>
    </div>
  );
}
