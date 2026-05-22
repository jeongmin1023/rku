"use client";

import { BookOpenCheck, ChevronLeft, FlaskConical, GitCompare, Search, ShieldCheck, Sparkles, X } from "lucide-react";
import { FormEvent, useMemo, useState } from "react";

import { ComparePanel } from "@/components/ComparePanel";
import { CrawlReview } from "@/components/CrawlReview";
import { HarvestProgress } from "@/components/HarvestProgress";
import { ProfessorCards, type FilterKey } from "@/components/ProfessorCards";
import { ProfessorDetail } from "@/components/ProfessorDetail";
import { Badge } from "@/components/Badge";
import { ErrorState } from "@/components/StateBlocks";
import {
  analyzeFit,
  confirmProfessors,
  crawlDepartment,
  fetchContactCard,
  fetchProfessorCards,
  fetchProfessorDetail,
  harvestDepartment,
  isMockMode
} from "@/lib/api";
import type {
  AppStep,
  ConfirmProfessor,
  ContactCard,
  CrawlResponse,
  FitResult,
  HarvestDepartmentResponse,
  HarvestProfessorResult,
  ProfessorCard,
  ProfessorDetail as ProfessorDetailType
} from "@/lib/types";

export default function Home() {
  const [step, setStep] = useState<AppStep>("onboarding");
  const [university, setUniversity] = useState("샘플대학교");
  const [department, setDepartment] = useState("컴퓨터공학과");
  const [url, setUrl] = useState("https://example.edu/faculty");
  const [interest, setInterest] = useState("LLM 기반 교육 서비스");
  const [crawl, setCrawl] = useState<CrawlResponse | null>(null);
  const [draft, setDraft] = useState<ConfirmProfessor[]>([]);
  const [harvestResult, setHarvestResult] = useState<HarvestDepartmentResponse | null>(null);
  const [cards, setCards] = useState<ProfessorCard[]>([]);
  const [filter, setFilter] = useState<FilterKey>("all");
  const [selectedDetailId, setSelectedDetailId] = useState<number | null>(null);
  const [details, setDetails] = useState<Record<number, ProfessorDetailType>>({});
  const [compareIds, setCompareIds] = useState<number[]>([]);
  const [fitByProfessor, setFitByProfessor] = useState<Record<number, FitResult>>({});
  const [contactByProfessor, setContactByProfessor] = useState<Record<number, ContactCard>>({});
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const selectedDetail = selectedDetailId ? details[selectedDetailId] : null;
  const compareDetails = compareIds.map((id) => details[id]).filter(Boolean);
  const harvestCounts = useMemo(() => {
    const map = new Map<number, HarvestProfessorResult>();
    harvestResult?.results.forEach((result) => map.set(result.professor.id, result));
    return map;
  }, [harvestResult]);

  async function handleCrawl(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading("crawl");
    try {
      const result = await crawlDepartment({ university, department, url });
      setCrawl(result);
      setDraft(
        result.professors.map((professor) => ({
          name: professor.name,
          english_name: professor.english_name,
          title: professor.title,
          lab_name: professor.lab_name,
          email: professor.email,
          profile_url: professor.profile_url,
          lab_url: professor.lab_url,
          official_keywords: professor.official_keywords,
          extraction_confidence: professor.extraction_confidence,
          excluded: false
        }))
      );
      setStep("review");
    } catch (caught) {
      setError(messageFromError(caught, "크롤링 요청에 실패했습니다."));
    } finally {
      setLoading(null);
    }
  }

  async function handleHarvest() {
    if (!crawl) return;
    setError(null);
    setLoading("harvest");
    setStep("harvesting");
    try {
      const includedNames = new Set(draft.filter((item) => !item.excluded).map((item) => item.name.trim()));
      await confirmProfessors(crawl.department.id, draft);
      const result = await harvestDepartment(crawl.department.id);
      const filteredResult = {
        ...result,
        results: result.results.filter((item) => includedNames.has(item.professor.name))
      };
      setHarvestResult(filteredResult);
      const fetchedCards = await fetchProfessorCards(crawl.department.id);
      setCards(
        fetchedCards
          .filter((card) => includedNames.has(card.name))
          .map((card) => enrichCardWithHarvest(card, filteredResult.results))
          .sort((left, right) => left.name.localeCompare(right.name, "ko"))
      );
      setStep("cards");
    } catch (caught) {
      setError(messageFromError(caught, "논문 수집 요청에 실패했습니다."));
      setStep("review");
    } finally {
      setLoading(null);
    }
  }

  async function openDetail(id: number) {
    setError(null);
    setLoading(`detail-${id}`);
    try {
      const detail = details[id] ?? (await fetchProfessorDetail(id));
      setDetails((prev) => ({ ...prev, [id]: detail }));
      setSelectedDetailId(id);
    } catch (caught) {
      setError(messageFromError(caught, "교수님 상세 정보를 가져오지 못했습니다."));
    } finally {
      setLoading(null);
    }
  }

  async function toggleCompare(id: number) {
    if (compareIds.includes(id)) {
      setCompareIds((prev) => prev.filter((item) => item !== id));
      return;
    }
    if (compareIds.length >= 3) return;
    if (!details[id]) {
      await openDetail(id);
    }
    setCompareIds((prev) => (prev.includes(id) ? prev : [...prev, id]));
  }

  async function handleFit(professorId: number, userInterest: string) {
    setError(null);
    setLoading(`fit-${professorId}`);
    try {
      const result = await analyzeFit(professorId, userInterest);
      setFitByProfessor((prev) => ({ ...prev, [professorId]: result }));
    } catch (caught) {
      setError(messageFromError(caught, "연구핏 분석에 실패했습니다."));
    } finally {
      setLoading(null);
    }
  }

  async function handleContact(professorId: number, userInterest: string) {
    setError(null);
    setLoading(`contact-${professorId}`);
    try {
      const result = await fetchContactCard(professorId, userInterest);
      setContactByProfessor((prev) => ({ ...prev, [professorId]: result }));
    } catch (caught) {
      setError(messageFromError(caught, "컨택 준비 카드 생성에 실패했습니다."));
    } finally {
      setLoading(null);
    }
  }

  return (
    <main className="min-h-screen bg-[#2E2838] text-[#F0EDE8]">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 py-5 sm:px-6 lg:px-8">
        <AppHeader step={selectedDetail ? "detail" : step} compareCount={compareIds.length} />

        {error ? (
          <div className="fixed left-4 right-4 top-20 z-30 mx-auto max-w-3xl">
            <ErrorState message={error} />
          </div>
        ) : null}

        <div className="flex flex-1 items-stretch py-5">
          {step === "onboarding" ? (
            <StepFrame tone="hero">
              <OnboardingPanel
                university={university}
                department={department}
                url={url}
                interest={interest}
                loading={loading === "crawl"}
                onUniversityChange={setUniversity}
                onDepartmentChange={setDepartment}
                onUrlChange={setUrl}
                onInterestChange={setInterest}
                onSubmit={handleCrawl}
              />
            </StepFrame>
          ) : null}

          {crawl && step === "review" ? (
            <StepFrame>
              <CrawlReview crawl={crawl} draft={draft} onDraftChange={setDraft} onHarvest={handleHarvest} loading={loading === "harvest"} />
            </StepFrame>
          ) : null}

          {step === "harvesting" ? (
            <StepFrame>
              <HarvestProgress harvesting={loading === "harvest"} result={harvestResult} draft={draft.filter((item) => !item.excluded)} />
            </StepFrame>
          ) : null}

          {step === "cards" && !selectedDetail ? (
            <StepFrame>
              <ProfessorCards
                cards={cards.map((card) => enrichCardWithHarvest(card, harvestResult?.results ?? []))}
                filter={filter}
                onFilterChange={setFilter}
                onOpenDetail={openDetail}
                compareIds={compareIds}
                onToggleCompare={toggleCompare}
                userInterest={interest}
              />
            </StepFrame>
          ) : null}

          {selectedDetail ? (
            <StepFrame>
              <div className="space-y-5">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <button
                    className="focus-ring inline-flex items-center gap-2 self-start rounded-md border border-warm-gray/20 bg-dark-purple px-3 py-2 text-sm font-semibold text-[#F0EDE8] transition duration-150 hover:scale-[1.02] hover:bg-dark-green"
                    type="button"
                    onClick={() => setSelectedDetailId(null)}
                  >
                    <ChevronLeft className="h-4 w-4" aria-hidden />
                    카드 목록으로
                  </button>
                  <button
                    className="focus-ring inline-flex h-9 w-9 items-center justify-center self-start rounded-md border border-warm-gray/20 bg-dark-purple text-warm-gray transition duration-150 hover:scale-[1.04] hover:bg-dark-green hover:text-white sm:self-auto"
                    type="button"
                    onClick={() => setSelectedDetailId(null)}
                    title="상세 닫기"
                  >
                    <X className="h-4 w-4" aria-hidden />
                  </button>
                </div>
                <ProfessorDetail
                  detail={selectedDetail}
                  initialInterest={interest}
                  fit={fitByProfessor[selectedDetail.id]}
                  contact={contactByProfessor[selectedDetail.id]}
                  loadingFit={loading === `fit-${selectedDetail.id}`}
                  loadingContact={loading === `contact-${selectedDetail.id}`}
                  error={null}
                  onAnalyzeFit={(nextInterest) => handleFit(selectedDetail.id, nextInterest)}
                  onBuildContact={(nextInterest) => handleContact(selectedDetail.id, nextInterest)}
                />
                <ComparePanel
                  details={compareDetails}
                  fitByProfessor={fitByProfessor}
                  onRemove={(id) => setCompareIds((prev) => prev.filter((item) => item !== id))}
                />
              </div>
            </StepFrame>
          ) : null}
        </div>
      </div>
    </main>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = "text"
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  type?: string;
}) {
  return (
    <label className="block">
      <span className="text-sm font-semibold text-[#F0EDE8]">{label}</span>
      <input
        className="focus-ring mt-2 min-h-11 w-full rounded-md border border-warm-gray/20 bg-[#2E2838] px-3 text-sm text-white placeholder:text-warm-gray"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        type={type}
        required={label !== "관심 연구주제"}
      />
    </label>
  );
}

function AppHeader({ step, compareCount }: { step: AppStep | "detail"; compareCount: number }) {
  const items = [
    { key: "onboarding", label: "Onboarding", icon: <Search className="h-4 w-4" /> },
    { key: "review", label: "CrawlReview", icon: <ShieldCheck className="h-4 w-4" /> },
    { key: "harvesting", label: "Harvest", icon: <BookOpenCheck className="h-4 w-4" /> },
    { key: "cards", label: "ProfessorCards", icon: <GitCompare className="h-4 w-4" /> },
    { key: "detail", label: "Detail/Fit", icon: <Sparkles className="h-4 w-4" /> }
  ] as const;

  return (
    <header className="sticky top-0 z-20 -mx-4 border-b border-warm-gray/20 bg-[#2E2838]/95 px-4 py-4 backdrop-blur sm:-mx-6 sm:px-6 lg:-mx-8 lg:px-8">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-gold text-[#1E2420] shadow-soft">
            <FlaskConical className="h-5 w-5" aria-hidden />
          </div>
          <div>
            <p className="text-sm font-bold text-gold">LabFit</p>
            <p className="text-xs text-warm-gray">공개 근거 기반 연구실 방향 탐색</p>
          </div>
        </div>
        <ol className="flex gap-2 overflow-x-auto pb-1">
        {items.map((item) => (
          <li key={item.key} className="flex-none">
            <span className={`inline-flex items-center gap-2 rounded-md border px-3 py-2 text-xs font-semibold transition duration-150 ${
              step === item.key ? "border-gold bg-gold text-[#1E2420]" : "border-warm-gray/20 bg-dark-purple text-warm-gray"
            }`}>
              {item.icon}
              {item.label}
            </span>
          </li>
        ))}
      </ol>
        <div className="flex flex-wrap gap-2">
          <Badge tone={isMockMode() ? "gold" : "green"}>{isMockMode() ? "Mock Mode" : "Backend API"}</Badge>
          <Badge tone="purple">비교 {compareCount}/3</Badge>
        </div>
      </div>
    </header>
  );
}

function StepFrame({ children, tone = "surface" }: { children: React.ReactNode; tone?: "surface" | "hero" }) {
  return (
    <section className={`step-enter min-h-[calc(100vh-116px)] w-full rounded-md border border-warm-gray/20 shadow-glow ${
      tone === "hero" ? "bg-gradient-to-br from-[#2E2838] to-[#1E2420]" : "bg-[#2E2838]"
    }`}>
      <div className="mx-auto flex min-h-[calc(100vh-116px)] w-full max-w-6xl flex-col justify-center px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </div>
    </section>
  );
}

function OnboardingPanel({
  university,
  department,
  url,
  interest,
  loading,
  onUniversityChange,
  onDepartmentChange,
  onUrlChange,
  onInterestChange,
  onSubmit
}: {
  university: string;
  department: string;
  url: string;
  interest: string;
  loading: boolean;
  onUniversityChange: (value: string) => void;
  onDepartmentChange: (value: string) => void;
  onUrlChange: (value: string) => void;
  onInterestChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <section className="mx-auto grid w-full max-w-5xl gap-8 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
      <div>
        <p className="text-sm font-bold uppercase tracking-[0.12em] text-gold">LabFit</p>
        <h1 className="mt-4 max-w-xl text-4xl font-bold leading-tight text-white sm:text-5xl">
          연구실 방향을 한 화면씩 가볍게 좁혀갑니다
        </h1>
        <p className="mt-5 max-w-lg text-sm leading-7 text-warm-gray">
          교수소개 페이지에서 후보를 추출하고, 논문 근거를 정리한 뒤, 내 관심 주제와 맞닿는 지점을 확인합니다.
        </p>
        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          <InfoBlock title="후보 추출" text="이름·링크·연구분야를 먼저 확인합니다." />
          <InfoBlock title="논문 정리" text="중복 후보를 병합하고 근거 상태를 나눕니다." />
          <InfoBlock title="핏 분석" text="관심 주제와 이어지는 키워드를 봅니다." />
        </div>
      </div>
      <form className="rounded-md border border-warm-gray/20 bg-dark-purple p-5 shadow-glow" onSubmit={onSubmit}>
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.12em] text-gold">Onboarding</p>
            <h2 className="mt-1 text-xl font-semibold text-white">학과 정보 입력</h2>
          </div>
          <Badge tone="purple">Step 1</Badge>
        </div>
        <div className="mt-5 space-y-4">
          <Field label="학교명" value={university} onChange={onUniversityChange} placeholder="예: 샘플대학교" />
          <Field label="학과명" value={department} onChange={onDepartmentChange} placeholder="예: 컴퓨터공학과" />
          <Field label="교수소개 페이지 URL" value={url} onChange={onUrlChange} placeholder="https://..." type="url" />
          <label className="block">
            <span className="text-sm font-semibold text-[#F0EDE8]">관심 연구주제</span>
            <textarea
              className="focus-ring mt-2 min-h-24 w-full resize-y rounded-md border border-warm-gray/20 bg-[#2E2838] px-3 py-2 text-sm leading-6 text-white placeholder:text-warm-gray"
              value={interest}
              onChange={(event) => onInterestChange(event.target.value)}
              placeholder="예: LLM 기반 교육 서비스"
            />
          </label>
          <button
            className="focus-ring inline-flex w-full items-center justify-center gap-2 rounded-md bg-gold px-4 py-3 text-sm font-bold text-[#1E2420] transition duration-150 hover:scale-[1.02] hover:bg-[#C89A5E] disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            disabled={loading}
          >
            <Search className="h-4 w-4" />
            {loading ? "교수님 목록 확인 중" : "교수님 목록 가져오기"}
          </button>
        </div>
      </form>
    </section>
  );
}

function InfoBlock({ title, text }: { title: string; text: string }) {
  return (
    <div className="rounded-md border border-warm-gray/20 bg-dark-purple/70 p-4 shadow-soft">
      <h3 className="text-sm font-semibold text-white">{title}</h3>
      <p className="mt-2 text-xs leading-5 text-warm-gray">{text}</p>
      </div>
  );
}

function enrichCardWithHarvest(card: ProfessorCard, results: HarvestProfessorResult[]): ProfessorCard {
  const result = results.find(
    (item) => item.professor.id === card.id || item.professor.name === card.name
  );

  if (!result) return card;

  const analysisReadyCount =
    result.analysis_ready_count ?? result.accepted_count + result.needs_review_count;

  const reviewCandidateCount =
    result.review_candidate_count ?? result.needs_review_count + result.weak_candidate_count;

  const candidatePoolCount =
    result.candidate_pool_count ??
    result.accepted_count + result.needs_review_count + result.weak_candidate_count;

  const excludedCount = result.excluded_count ?? result.rejected_count;

  return {
    ...card,

    accepted_count: result.accepted_count,
    needs_review_count: result.needs_review_count,
    weak_candidate_count: result.weak_candidate_count,
    rejected_count: result.rejected_count,
    accepted_paper_count: result.accepted_count,
    needs_review_paper_count: result.needs_review_count,
    rejected_paper_count: result.rejected_count,

    source_candidate_count: result.source_candidate_count,
    master_paper_count: result.master_paper_count,

    analysis_ready_count: analysisReadyCount,
    review_candidate_count: reviewCandidateCount,
    candidate_pool_count: candidatePoolCount,
    excluded_count: excludedCount,
    warning_count: result.warning_count ?? 0,

    usable_rate: result.usable_rate ?? 0,
    candidate_pool_rate: result.candidate_pool_rate ?? 0,
    excluded_rate: result.excluded_rate ?? 0,

    keywords: result.analysis.five_year_keywords.slice(0, 5),
    trend_summary: result.analysis.trend_summary,
    recent_keywords: result.analysis.recent_keywords,
    five_year_keywords: result.analysis.five_year_keywords,
    overall_keywords: result.analysis.overall_keywords,
    trend_confidence: result.analysis.trend_confidence,
    warnings: result.analysis.warnings,
    evidence_confidence: result.analysis.evidence_confidence,
    analysis_type: result.professor.analysis_type || card.analysis_type,
  };
}

function messageFromError(error: unknown, fallback: string) {
  if (error instanceof Error && error.message) return error.message;
  return fallback;
}
