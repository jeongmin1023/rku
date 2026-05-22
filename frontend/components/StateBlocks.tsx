import { AlertTriangle, Inbox } from "lucide-react";

export function ErrorState({ title = "요청을 처리하지 못했습니다.", message }: { title?: string; message?: string }) {
  return (
    <div className="flex gap-3 rounded-md border border-gold/30 bg-dark-purple p-4 text-[#F0EDE8] shadow-soft">
      <AlertTriangle className="mt-0.5 h-5 w-5 flex-none text-gold" aria-hidden />
      <div>
        <p className="text-sm font-semibold">{title}</p>
        {message ? <p className="mt-1 text-sm leading-6 text-warm-gray">{message}</p> : null}
      </div>
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex gap-3 rounded-md border border-dashed border-warm-gray/25 bg-dark-purple/70 p-5 text-[#F0EDE8]">
      <Inbox className="mt-0.5 h-5 w-5 flex-none text-purple" aria-hidden />
      <p className="text-sm leading-6">{message}</p>
    </div>
  );
}

export function SectionTitle({ eyebrow, title, description }: { eyebrow?: string; title: string; description?: string }) {
  return (
    <div>
      {eyebrow ? <p className="text-xs font-semibold uppercase tracking-[0.12em] text-gold">{eyebrow}</p> : null}
      <h2 className="mt-1 text-xl font-semibold text-white">{title}</h2>
      {description ? <p className="mt-2 max-w-3xl text-sm leading-6 text-warm-gray">{description}</p> : null}
    </div>
  );
}
