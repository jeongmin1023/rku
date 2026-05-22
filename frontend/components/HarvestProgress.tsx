import { AlertTriangle, CheckCircle2, Database, Loader2, ShieldCheck, XCircle } from "lucide-react";

import { Badge } from "@/components/Badge";
import { SectionTitle } from "@/components/StateBlocks";
import type { HarvestDepartmentResponse, HarvestProfessorResult } from "@/lib/types";

export function HarvestProgress({ harvesting, result }: { harvesting: boolean; result?: HarvestDepartmentResponse | null }) {
  return (
    <section className="space-y-5">
      <SectionTitle
        eyebrow="Paper Harvest"
        title="논문 수집 중간 정리"
        description="여러 국내 학술 데이터 소스에서 가져온 후보를 표준화하고 중복 병합한 뒤, 교수님과의 매칭 근거를 계산합니다."
      />

      {harvesting ? (
        <div className="rounded-md border border-line bg-white p-5 shadow-soft">
          <div className="flex items-center gap-3">
            <Loader2 className="h-5 w-5 animate-spin text-bluepoint" />
            <div>
              <p className="font-semibold text-navy-900">수집과 병합을 진행 중입니다.</p>
              <p className="mt-1 text-sm leading-6 text-slate-600">
                KCI, RISS, DBpia, ScienceON 등 국내 학술 데이터 소스에서 논문 후보를 수집하고 있습니다.
              </p>
            </div>
          </div>
        </div>
      ) : null}

      {result ? (
        <div className="space-y-4">
          {result.results.map((item) => (
            <ProfessorHarvestSummary key={item.professor.id} item={item} />
          ))}
        </div>
      ) : null}
    </section>
  );
}

function ProfessorHarvestSummary({ item }: { item: HarvestProfessorResult }) {
  const accepted = item.accepted_count ?? 0;
  const needsReview = item.needs_review_count ?? 0;
  const weak = item.weak_candidate_count ?? 0;
  const rejected = item.rejected_count ?? 0;
  const analysisReady = item.analysis_ready_count ?? accepted + needsReview;
  const reviewCandidates = item.review_candidate_count ?? needsReview + weak;
  const candidatePool = item.candidate_pool_count ?? accepted + needsReview + weak;
  const excluded = item.excluded_count ?? rejected;
  const warningCount = item.warning_count ?? 0;
  const masterCount = item.master_paper_count ?? 0;
  const usableRate = item.usable_rate ?? percent(analysisReady, masterCount);
  const candidatePoolRate = item.candidate_pool_rate ?? percent(candidatePool, masterCount);
  const excludedRate = item.excluded_rate ?? percent(excluded, masterCount);
  const statusLabel = analysisReady > 0 ? "분석 사용 가능" : candidatePool > 0 ? "검증 후 사용 가능" : "매칭 근거 확인 필요";

  return (
    <article className="rounded-md border border-line bg-white p-5 shadow-soft">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-lg font-bold text-navy-900">{item.professor.name}</h3>
            <Badge>{statusLabel}</Badge>
          </div>
          <p className="mt-1 text-sm text-slate-600">{item.professor.lab_name || "연구실명 확인 필요"}</p>
        </div>
        <div className="text-sm text-slate-600">
          분석 사용 가능률 <span className="font-bold text-navy-900">{usableRate}%</span>
        </div>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-4">
        <Metric icon={<Database className="h-4 w-4" />} label="원본 후보" value={item.source_candidate_count} help="학술 데이터 소스에서 처음 가져온 후보" />
        <Metric icon={<Database className="h-4 w-4" />} label="중복 정리" value={masterCount} help="중복을 병합한 MasterPaper" />
        <Metric icon={<CheckCircle2 className="h-4 w-4" />} label="분석 사용 가능" value={analysisReady} help="accepted + needs_review" />
        <Metric icon={<AlertTriangle className="h-4 w-4" />} label="검증 후보" value={reviewCandidates} help="needs_review + weak_candidate" />
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <Metric icon={<ShieldCheck className="h-4 w-4" />} label="accepted" value={accepted} help="분석에 바로 사용할 수 있는 후보" />
        <Metric icon={<AlertTriangle className="h-4 w-4" />} label="검증 필요" value={needsReview} help="근거 확인 후 볼 후보" />
        <Metric icon={<AlertTriangle className="h-4 w-4" />} label="낮은 신뢰도 후보" value={weak} help="보조 후보로만 보존" />
        <Metric icon={<XCircle className="h-4 w-4" />} label="분석 제외" value={excluded} help="rejected" />
      </div>

      <div className="mt-5 rounded-md bg-mist p-4 text-sm leading-6 text-slate-700">
        <p>
          <strong className="text-navy-900">해석:</strong> 총 {masterCount}개의 정리된 논문 중 {analysisReady}개는 분석에 사용하고,
          {reviewCandidates}개는 검증 후보로 남겼으며, {excluded}개는 기본 분석에서 제외했습니다.
        </p>
        <p className="mt-1">
          후보 보존율은 {candidatePoolRate}%이고, 제외율은 {excludedRate}%입니다. 확인 필요 메시지는 {warningCount}개입니다.
        </p>
      </div>
    </article>
  );
}

function Metric({ icon, label, value, help }: { icon: React.ReactNode; label: string; value: number; help: string }) {
  return (
    <div className="rounded-md border border-line bg-white p-4">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
        {icon}
        {label}
      </div>
      <div className="mt-2 text-2xl font-bold text-navy-900">{value ?? 0}</div>
      <p className="mt-1 text-xs leading-5 text-slate-500">{help}</p>
    </div>
  );
}

function percent(value: number, total: number) {
  if (!total) return 0;
  return Math.round((value / total) * 1000) / 10;
}
