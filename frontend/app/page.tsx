"use client";

import { BookOpenCheck, FlaskConical, GitCompare, Loader2, Search, ShieldCheck } from "lucide-react";
import { FormEvent, useMemo, useState } from "react";

import { ComparePanel } from "@/components/ComparePanel";
import { CrawlReview } from "@/components/CrawlReview";
import { HarvestProgress } from "@/components/HarvestProgress";
import { ProfessorCards, type FilterKey } from "@/components/ProfessorCards";
import { ProfessorDetail } from "@/components/ProfessorDetail";
import { Badge } from "@/components/Badge";
import { ErrorState, SectionTitle } from "@/components/StateBlocks";
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
    <main className="min-h-screen">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-4 py-6 sm:px-6 lg:px-8">
        <header className="flex flex-col gap-5 border-b border-line pb-6 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-md bg-navy-900 text-white">
                <FlaskConical className="h-5 w-5" aria-hidden />
              </div>
              <div>
                <p className="text-sm font-semibold text-bluepoint">LabFit</p>
                <h1 className="text-2xl font-semibold text-navy-900">연구실 방향 탐색 도구</h1>
              </div>
            </div>
            <p className="mt-4 max-w-4xl text-sm leading-6 text-slate-700">
              LabFit은 교수님을 평가하거나 순위를 매기는 서비스가 아닙니다. 공개 논문·연구실 정보를 바탕으로 사용자의 관심 주제와 연구실 방향의 연결성을 분석합니다.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge tone={isMockMode() ? "amber" : "green"}>{isMockMode() ? "Mock Mode" : "Backend API"}</Badge>
            <Badge tone="blue">근거 중심</Badge>
            <Badge tone="slate">우열 비교 없음</Badge>
          </div>
        </header>

        {error ? <ErrorState message={error} /> : null}

        <section className="grid gap-6 lg:grid-cols-[390px_1fr]">
          <aside className="space-y-5">
            <form className="rounded-md border border-line bg-white p-5 shadow-soft" onSubmit={handleCrawl}>
              <SectionTitle eyebrow="Start" title="학과 정보 입력" description="교수소개 페이지 URL을 넣으면 교수님 후보를 먼저 추출합니다." />
              <div className="mt-5 space-y-4">
                <Field label="학교명" value={university} onChange={setUniversity} placeholder="예: 샘플대학교" />
                <Field label="학과명" value={department} onChange={setDepartment} placeholder="예: 컴퓨터공학과" />
                <Field label="교수소개 페이지 URL" value={url} onChange={setUrl} placeholder="https://..." type="url" />
                <label className="block">
                  <span className="text-sm font-semibold text-navy-900">관심 연구주제, 선택 입력</span>
                  <textarea
                    className="focus-ring mt-2 min-h-24 w-full resize-y rounded-md border border-line bg-white px-3 py-2 text-sm leading-6"
                    value={interest}
                    onChange={(event) => setInterest(event.target.value)}
                    placeholder="예: LLM 기반 교육 서비스"
                  />
                </label>
                <button
                  className="focus-ring inline-flex w-full items-center justify-center gap-2 rounded-md bg-navy-900 px-4 py-3 text-sm font-semibold text-white hover:bg-navy-800 disabled:cursor-not-allowed disabled:bg-slate-400"
                  type="submit"
                  disabled={loading === "crawl"}
                >
                  {loading === "crawl" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                  교수님 목록 가져오기
                </button>
              </div>
            </form>

            <WorkflowRail step={step} compareCount={compareIds.length} />
          </aside>

          <div className="space-y-8">
            {step === "onboarding" ? <OnboardingPanel /> : null}

            {crawl && step === "review" ? (
              <CrawlReview crawl={crawl} draft={draft} onDraftChange={setDraft} onHarvest={handleHarvest} loading={loading === "harvest"} />
            ) : null}

            {step === "harvesting" ? <HarvestProgress harvesting={loading === "harvest"} result={harvestResult} /> : null}

            {step === "cards" ? (
              <>
                <HarvestProgress harvesting={false} result={harvestResult} />
                <ProfessorCards
                  cards={cards.map((card) => enrichCardWithHarvest(card, harvestResult?.results ?? []))}
                  filter={filter}
                  onFilterChange={setFilter}
                  onOpenDetail={openDetail}
                  compareIds={compareIds}
                  onToggleCompare={toggleCompare}
                  userInterest={interest}
                />
                <ComparePanel
                  details={compareDetails}
                  fitByProfessor={fitByProfessor}
                  onRemove={(id) => setCompareIds((prev) => prev.filter((item) => item !== id))}
                />
              </>
            ) : null}

            {selectedDetail ? (
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
            ) : null}
          </div>
        </section>
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
      <span className="text-sm font-semibold text-navy-900">{label}</span>
      <input
        className="focus-ring mt-2 min-h-11 w-full rounded-md border border-line bg-white px-3 text-sm"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        type={type}
        required={label !== "관심 연구주제"}
      />
    </label>
  );
}

function WorkflowRail({ step, compareCount }: { step: AppStep; compareCount: number }) {
  const items = [
    { key: "onboarding", label: "입력", icon: <Search className="h-4 w-4" /> },
    { key: "review", label: "크롤링 확인", icon: <ShieldCheck className="h-4 w-4" /> },
    { key: "harvesting", label: "논문 수집", icon: <BookOpenCheck className="h-4 w-4" /> },
    { key: "cards", label: "연구 방향 탐색", icon: <GitCompare className="h-4 w-4" /> }
  ] as const;

  return (
    <div className="rounded-md border border-line bg-white p-5 shadow-soft">
      <h2 className="text-sm font-semibold text-navy-900">진행 상태</h2>
      <ol className="mt-4 space-y-3">
        {items.map((item) => (
          <li key={item.key} className={`flex items-center gap-3 text-sm ${step === item.key ? "font-semibold text-navy-900" : "text-slate-600"}`}>
            <span className={`flex h-8 w-8 items-center justify-center rounded-md ${step === item.key ? "bg-bluepoint text-white" : "bg-mist text-slate-600"}`}>
              {item.icon}
            </span>
            {item.label}
          </li>
        ))}
      </ol>
      <p className="mt-4 border-t border-line pt-4 text-sm leading-6 text-slate-600">
        비교 선택 {compareCount}/3명. 비교는 우열 판단이 아니라 연구 방향을 나란히 보는 기능입니다.
      </p>
    </div>
  );
}

function OnboardingPanel() {
  return (
    <section className="space-y-5">
      <SectionTitle
        eyebrow="Welcome"
        title="먼저 교수소개 페이지를 확인합니다"
        description="크롤링 결과는 바로 확정하지 않고 사용자가 확인할 수 있게 보여줍니다. 이후 여러 데이터 소스의 논문 후보를 표준화하고, 중복 병합과 매칭 근거 계산을 거칩니다."
      />
      <div className="grid gap-4 md:grid-cols-3">
        <InfoBlock title="후보 추출" text="이름, 이메일, 연구분야, 상세 링크 주변 텍스트를 바탕으로 교수님 후보를 찾습니다." />
        <InfoBlock title="논문 병합" text="KCI, OpenAlex, Crossref 후보를 표준화한 뒤 DOI/UCI/제목/저자/연도 기준으로 MasterPaper를 만듭니다." />
        <InfoBlock title="근거 중심 해석" text="accepted와 검증 필요 논문을 분리하고, 공개 데이터가 부족하면 Emerging Lab으로 표시합니다." />
      </div>
    </section>
  );
}

function InfoBlock({ title, text }: { title: string; text: string }) {
  return (
    <div className="rounded-md border border-line bg-white p-5 shadow-soft">
      <h3 className="text-base font-semibold text-navy-900">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-600">{text}</p>
    </div>
  );
}

function enrichCardWithHarvest(card: ProfessorCard, results: HarvestProfessorResult[]): ProfessorCard {
  const result = results.find((item) => item.professor.id === card.id || item.professor.name === card.name);
  if (!result) return card;
  return {
    ...card,
    accepted_count: result.accepted_count,
    needs_review_count: result.needs_review_count,
    rejected_count: result.rejected_count,
    source_candidate_count: result.source_candidate_count,
    master_paper_count: result.master_paper_count,
    keywords: result.analysis.five_year_keywords.slice(0, 5),
    trend_summary: result.analysis.trend_summary,
    warnings: result.analysis.warnings,
    evidence_confidence: result.analysis.evidence_confidence,
    analysis_type: result.professor.analysis_type || card.analysis_type
  };
}

function messageFromError(error: unknown, fallback: string) {
  if (error instanceof Error && error.message) return error.message;
  return fallback;
}
