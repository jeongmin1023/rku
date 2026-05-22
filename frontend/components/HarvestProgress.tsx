import { AlertTriangle, CheckCircle2, Database, Loader2 } from "lucide-react";

import { Badge } from "@/components/Badge";
import { SectionTitle } from "@/components/StateBlocks";
import type { HarvestDepartmentResponse } from "@/lib/types";

export function HarvestProgress({
  harvesting,
  result
}: {
  harvesting: boolean;
  result?: HarvestDepartmentResponse | null;
}) {
  return (
    <section className="space-y-5">
      <SectionTitle
        eyebrow="Paper Harvest"
        title="논문 후보 표준화와 매칭"
        description="여러 학술 데이터 소스에서 가져온 논문 후보를 표준화하고 중복 병합한 뒤, 교수님과의 매칭 신뢰도를 계산하고 있습니다."
      />

      {harvesting ? (
        <div className="rounded-md border border-line bg-white p-6 shadow-soft">
          <div className="flex items-center gap-3">
            <Loader2 className="h-5 w-5 animate-spin text-bluepoint" aria-hidden />
            <p className="text-sm font-semibold text-navy-900">수집과 병합을 진행 중입니다.</p>
          </div>
          <div className="mt-5 h-2 overflow-hidden rounded-full bg-mist">
            <div className="h-full w-2/3 rounded-full bg-bluepoint" />
          </div>
          <p className="mt-4 text-sm leading-6 text-slate-600">
            교수명만으로 논문을 확정하지 않고, 소속·키워드·식별자·출처 일치 신호를 함께 확인합니다.
          </p>
        </div>
      ) : null}

      {result ? (
        <div className="grid gap-4 md:grid-cols-3">
          {result.results.map((item) => {
            const warningCount = item.rejected_count + item.needs_review_count;
            return (
              <article key={item.professor.id} className="rounded-md border border-line bg-white p-4 shadow-soft">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="font-semibold text-navy-900">{item.professor.name}</h3>
                    <p className="mt-1 text-sm text-slate-600">{item.professor.lab_name || "연구실명 확인 필요"}</p>
                  </div>
                  <Badge tone={warningCount ? "amber" : "green"}>{warningCount ? "검증 항목 있음" : "기본 근거 확인"}</Badge>
                </div>

                <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
                  <Metric icon={<Database className="h-4 w-4" />} label="논문 후보" value={item.source_candidate_count} />
                  <Metric icon={<Database className="h-4 w-4" />} label="MasterPaper" value={item.master_paper_count} />
                  <Metric icon={<CheckCircle2 className="h-4 w-4" />} label="accepted" value={item.accepted_count} />
                  <Metric icon={<AlertTriangle className="h-4 w-4" />} label="needs_review" value={item.needs_review_count} />
                  <Metric icon={<AlertTriangle className="h-4 w-4" />} label="rejected" value={item.rejected_count} />
                  <Metric icon={<AlertTriangle className="h-4 w-4" />} label="오염 경고" value={warningCount} />
                </dl>
              </article>
            );
          })}
        </div>
      ) : null}
    </section>
  );
}

function Metric({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) {
  return (
    <div>
      <dt className="flex items-center gap-1.5 text-xs font-semibold text-slate-500">
        {icon}
        {label}
      </dt>
      <dd className="mt-1 text-lg font-semibold text-navy-900">{value}</dd>
    </div>
  );
}
