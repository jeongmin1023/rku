import { AlertTriangle, Inbox } from "lucide-react";

export function ErrorState({ title = "요청을 처리하지 못했습니다.", message }: { title?: string; message?: string }) {
  return (
    <div className="flex gap-3 rounded-md border border-rose-200 bg-rose-50 p-4 text-rose-900">
      <AlertTriangle className="mt-0.5 h-5 w-5 flex-none" aria-hidden />
      <div>
        <p className="text-sm font-semibold">{title}</p>
        {message ? <p className="mt-1 text-sm leading-6 text-rose-800">{message}</p> : null}
      </div>
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex gap-3 rounded-md border border-dashed border-line bg-white/60 p-5 text-navy-800">
      <Inbox className="mt-0.5 h-5 w-5 flex-none text-bluepoint" aria-hidden />
      <p className="text-sm leading-6">{message}</p>
    </div>
  );
}

export function SectionTitle({ eyebrow, title, description }: { eyebrow?: string; title: string; description?: string }) {
  return (
    <div>
      {eyebrow ? <p className="text-xs font-semibold uppercase tracking-[0.12em] text-bluepoint">{eyebrow}</p> : null}
      <h2 className="mt-1 text-xl font-semibold text-navy-900">{title}</h2>
      {description ? <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{description}</p> : null}
    </div>
  );
}
