import { ArrowUpRight } from "lucide-react";

function StatCard({ icon: Icon, label, value, change }) {
  return (
    <div className="group rounded-2xl border border-[#d7d1c4] bg-[#f9f6ee] p-5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[0_8px_30px_rgba(24,35,31,0.06)]">
      
      <div className="flex items-start justify-between">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#dceade] text-[#315846]">
          <Icon size={19} strokeWidth={1.7} />
        </div>

        <div className="flex items-center gap-1 text-[11px] font-medium text-[#347457]">
          <ArrowUpRight size={13} />
          {change}
        </div>
      </div>

      <p className="mt-5 text-[11px] uppercase tracking-[0.08em] text-[#727b75]">
        {label}
      </p>

      <p className="mt-1 font-['Space_Mono'] text-[24px] font-bold tracking-tight text-[#18231f]">
        {value}
      </p>
    </div>
  );
}

export default StatCard;