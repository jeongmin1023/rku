"use client";

import { CalendarDays, CheckCircle2, Loader2, Mail, MessageSquare, NotebookText, Search } from "lucide-react";
import { useMemo, useState } from "react";

import { AnalysisTypeBadge, ConfidenceBadge } from "@/components/Badge";
import { PaperCard } from "@/components/PaperCard";
import { EmptyState, ErrorState, SectionTitle } from "@/components/StateBlocks";
import type { ContactCard, FitResult, ProfessorDetail as ProfessorDetailType, ProfessorPaper } from "@/lib/types";

type TabKey = "summary" | "papers" | "fit" | "contact";

const tabs: Array<{ key: TabKey; label: string }> = [
  { key: "summary", label: "연구 요약" },
  { key: "papers", label: "논문" },
  { key: "fit", label: "내 관심 주제와 비교" },
  { key: "contact", label: "컨택 준비" }
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
  onBuildContact
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

  return (
    <section className="rounded-md border border-line bg-white p-5 shadow-soft">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-sm font-semibold text-bluepoint">{detail.department_info.university} · {detail.department_info.department}</p>
          <h2 className="mt-1 text-2xl font-semibold text-navy-900">{detail.name}</h2>
          <p className="mt-2 text-sm text-slate-600">{detail.lab_name || "연구실명 확인 필요"} · {detail.email || "이메일 확인 필요"}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <AnalysisTypeBadge type={detail.analysis_type} />
          <ConfidenceBadge confidence={detail.evidence_confidence} />
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-2 border-b border-line">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            className={`focus-ring -mb-px rounded-t-md border border-b-0 px-4 py-2 text-sm font-semibold ${
              activeTab === tab.key ? "border-line bg-ivory text-navy-900" : "border-transparent text-slate-600 hover:bg-mist"
            }`}
            onClick={() => setActiveTab(tab.key)}
            type="button"
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="mt-6">
        {error ? <ErrorState message={error} /> : null}
        {activeTab === "summary" ? <SummaryTab detail={detail} acceptedCount={accepted.length} needsReviewCount={needsReview.length} /> : null}
        {activeTab === "papers" ? <PapersTab detail={detail} papersById={papersById} fit={fit} /> : null}
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
      </div>
    </section>
  );
}

function SummaryTab({ detail, acceptedCount, needsReviewCount }: { detail: ProfessorDetailType; acceptedCount: number; needsReviewCount: number }) {
  const timelineEntries = Object.entries(detail.analysis.timeline);
  return (
    <div className="space-y-6">
      <SectionTitle title="연구 경향 요약" description={detail.analysis.trend_summary} />

      <div className="grid gap-4 lg:grid-cols-3">
        <KeywordBlock title="핵심 키워드" keywords={detail.analysis.overall_keywords} />
        <KeywordBlock title="최근 3년 키워드" keywords={detail.analysis.recent_keywords} />
        <KeywordBlock title="최근 5년 키워드" keywords={detail.analysis.five_year_keywords} />
      </div>

      <div className="grid gap-5 lg:grid-cols-[1.3fr_.7fr]">
        <div>
          <h3 className="text-base font-semibold text-navy-900">연구 흐름 타임라인</h3>
          {timelineEntries.length ? (
            <ol className="mt-4 space-y-3 border-l border-line pl-4">
              {timelineEntries.map(([year, keywords]) => (
                <li key={year}>
                  <p className="text-sm font-semibold text-navy-900">{year}</p>
                  <p className="mt-1 text-sm text-slate-600">{keywords.join(", ")}</p>
                </li>
              ))}
            </ol>
          ) : (
            <EmptyState message="연도별 연구 흐름을 만들 만큼 공개 논문 데이터가 충분하지 않습니다." />
          )}
        </div>

        <div>
          <h3 className="text-base font-semibold text-navy-900">근거 상태</h3>
          <dl className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between gap-4 border-b border-line pb-2">
              <dt className="text-slate-600">accepted 논문</dt>
              <dd className="font-semibold text-navy-900">{acceptedCount}</dd>
            </div>
            <div className="flex justify-between gap-4 border-b border-line pb-2">
              <dt className="text-slate-600">검증 필요 논문</dt>
              <dd className="font-semibold text-navy-900">{needsReviewCount}</dd>
            </div>
          </dl>
          <div className="mt-4 flex flex-wrap gap-2">
            <AnalysisTypeBadge type={detail.analysis_type} />
            <ConfidenceBadge confidence={detail.analysis.evidence_confidence} />
          </div>
        </div>
      </div>

      {detail.analysis.warnings.length ? (
        <div className="rounded-md border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-900">
          {detail.analysis.warnings.map((warning) => (
            <p key={warning}>{warning}</p>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function PapersTab({
  detail,
  papersById,
  fit
}: {
  detail: ProfessorDetailType;
  papersById: Map<number, ProfessorPaper>;
  fit?: FitResult | null;
}) {
  const representative = detail.analysis.representative_papers;
  const recent = detail.analysis.recent_papers;
  return (
    <div className="space-y-8">
      <PaperSection
        title="대표 논문"
        description="인용 신호, 연구실 핵심 키워드, 저자 역할, 매칭 근거를 함께 고려한 후보입니다."
        papers={representative}
        papersById={papersById}
      />
      <PaperSection
        title="최근 논문"
        description="최근 연구 방향을 보여주는 공개 논문 후보입니다."
        papers={recent}
        papersById={papersById}
      />
      <div className="space-y-3">
        <h3 className="text-base font-semibold text-navy-900">관심 주제 관련 논문</h3>
        {fit?.related_papers.length ? (
          <div className="grid gap-4">
            {fit.related_papers.map((paper) => {
              const linked = paper.id ? papersById.get(paper.id) : undefined;
              return linked ? (
                <PaperCard key={paper.id ?? paper.title} paper={linked} reason={paper.connection_reason} />
              ) : (
                <PaperCard key={paper.id ?? paper.title} paper={{ ...paper, citation_signals: {}, label: "관심 주제 관련", reason: paper.connection_reason }} />
              );
            })}
          </div>
        ) : (
          <EmptyState message="입력한 관심 주제와 직접적으로 가까운 공개 논문은 확인되지 않았습니다. 컨택 시 해당 주제 가능 여부를 확인하는 것이 좋습니다." />
        )}
      </div>
    </div>
  );
}

function PaperSection({
  title,
  description,
  papers,
  papersById
}: {
  title: string;
  description: string;
  papers: Array<{ id?: number; title?: string; reason?: string }>;
  papersById: Map<number, ProfessorPaper>;
}) {
  return (
    <div className="space-y-3">
      <div>
        <h3 className="text-base font-semibold text-navy-900">{title}</h3>
        <p className="mt-1 text-sm leading-6 text-slate-600">{description}</p>
      </div>
      {papers.length ? (
        <div className="grid gap-4">
          {papers.map((paper) => {
            const linked = paper.id ? papersById.get(paper.id) : undefined;
            return linked ? (
              <PaperCard key={paper.id ?? paper.title} paper={linked} reason={paper.reason} />
            ) : (
              <PaperCard key={paper.id ?? paper.title} paper={{ ...paper, citation_signals: {} }} />
            );
          })}
        </div>
      ) : (
        <EmptyState message="공개 논문 데이터가 충분하지 않습니다. 연구실 소개와 교수소개 페이지를 중심으로 확인하세요." />
      )}
    </div>
  );
}

function FitTab({
  interest,
  onInterestChange,
  fit,
  loading,
  onAnalyze
}: {
  interest: string;
  onInterestChange: (value: string) => void;
  fit?: FitResult | null;
  loading: boolean;
  onAnalyze: () => void;
}) {
  return (
    <div className="space-y-5">
      <SectionTitle
        title="내 관심 주제와 비교"
        description="숫자 중심 판단이 아니라 공개 논문과 관심 주제 사이의 연결 근거, 그리고 컨택 전 확인할 질문을 함께 봅니다."
      />
      <div className="flex flex-col gap-3 md:flex-row">
        <input
          className="focus-ring min-h-11 flex-1 rounded-md border border-line bg-white px-4 text-sm"
          value={interest}
          onChange={(event) => onInterestChange(event.target.value)}
          placeholder="예: LLM 기반 교육 서비스"
        />
        <button
          className="focus-ring inline-flex items-center justify-center gap-2 rounded-md bg-navy-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-navy-800 disabled:cursor-not-allowed disabled:bg-slate-400"
          type="button"
          onClick={onAnalyze}
          disabled={loading || !interest.trim()}
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          연구핏 분석하기
        </button>
      </div>

      {fit ? (
        <div className="space-y-5">
          <div className="rounded-md border border-line bg-ivory p-5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full border border-bluepoint/25 bg-bluepoint/10 px-3 py-1 text-sm font-semibold text-navy-800">{fit.fit_level}</span>
              <ConfidenceBadge confidence={fit.evidence_confidence} />
            </div>
            <p className="mt-4 text-sm leading-6 text-slate-700">{fit.interpretation}</p>
          </div>

          <KeywordBlock title="맞닿는 키워드" keywords={fit.matched_keywords} />

          <div className="grid gap-5 lg:grid-cols-2">
            <CheckList title="맞는 부분" icon={<CheckCircle2 className="h-4 w-4" />} items={fit.matched_keywords.map((keyword) => `${keyword} 관련 공개 연구 신호가 감지됩니다.`)} />
            <CheckList title="확인 필요한 부분" icon={<MessageSquare className="h-4 w-4" />} items={fit.check_points} />
          </div>
        </div>
      ) : (
        <EmptyState message="관심 주제를 입력하고 분석하면 해석, 맞닿는 키워드, 확인 필요 항목이 함께 표시됩니다." />
      )}
    </div>
  );
}

function ContactTab({
  interest,
  onInterestChange,
  contact,
  loading,
  onBuild
}: {
  interest: string;
  onInterestChange: (value: string) => void;
  contact?: ContactCard | null;
  loading: boolean;
  onBuild: () => void;
}) {
  return (
    <div className="space-y-5">
      <SectionTitle
        title="컨택 준비 카드"
        description="이 카드는 컨택 전 준비를 돕기 위한 참고 자료입니다. 실제 모집 주제와 연구실 운영 방식은 교수님께 직접 확인해야 합니다."
      />
      <div className="flex flex-col gap-3 md:flex-row">
        <input
          className="focus-ring min-h-11 flex-1 rounded-md border border-line bg-white px-4 text-sm"
          value={interest}
          onChange={(event) => onInterestChange(event.target.value)}
          placeholder="컨택에서 묻고 싶은 관심 주제"
        />
        <button
          className="focus-ring inline-flex items-center justify-center gap-2 rounded-md bg-navy-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-navy-800 disabled:cursor-not-allowed disabled:bg-slate-400"
          type="button"
          onClick={onBuild}
          disabled={loading || !interest.trim()}
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Mail className="h-4 w-4" />}
          카드 생성
        </button>
      </div>

      {contact ? (
        <div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
          <div>
            <h3 className="flex items-center gap-2 text-base font-semibold text-navy-900">
              <NotebookText className="h-4 w-4 text-bluepoint" />
              컨택 전 읽을 논문
            </h3>
            <div className="mt-3 space-y-3">
              {contact.reading_list.map((paper) => (
                <div key={`${paper.category}-${paper.title}`} className="border-b border-line pb-3">
                  <p className="text-xs font-semibold text-bluepoint">{paper.category}</p>
                  <p className="mt-1 text-sm font-semibold text-navy-900">{paper.title || "자료 확인 필요"}</p>
                  <p className="mt-1 text-sm leading-6 text-slate-600">{paper.why_read}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="space-y-5">
            <CheckList title="교수님께 물어볼 질문" icon={<MessageSquare className="h-4 w-4" />} items={contact.questions} />
            <CheckList title="메일에 넣을 연구 포인트" icon={<CalendarDays className="h-4 w-4" />} items={contact.email_points} />
            <CheckList title="확인 필요 항목" icon={<CheckCircle2 className="h-4 w-4" />} items={contact.check_points} />
          </div>
        </div>
      ) : (
        <EmptyState message="관심 주제를 입력하고 컨택 준비 카드를 생성하면 읽을 논문, 질문, 메일 포인트가 정리됩니다." />
      )}
    </div>
  );
}

function KeywordBlock({ title, keywords }: { title: string; keywords: string[] }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-navy-900">{title}</h3>
      {keywords.length ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {keywords.map((keyword) => (
            <span key={keyword} className="rounded-full bg-mist px-2.5 py-1 text-xs font-semibold text-slate-700">
              {keyword}
            </span>
          ))}
        </div>
      ) : (
        <p className="mt-3 text-sm text-slate-500">키워드 확인 필요</p>
      )}
    </div>
  );
}

function CheckList({ title, icon, items }: { title: string; icon: React.ReactNode; items: string[] }) {
  return (
    <div>
      <h3 className="flex items-center gap-2 text-base font-semibold text-navy-900">
        {icon}
        {title}
      </h3>
      {items.length ? (
        <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-700">
          {items.map((item) => (
            <li key={item} className="border-b border-line pb-2 last:border-0">
              {item}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-slate-500">확인된 항목이 없습니다.</p>
      )}
    </div>
  );
}
