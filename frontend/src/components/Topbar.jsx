import { Bell, ChevronDown, Sparkles } from "lucide-react";

function Topbar() {
  return (
    <header className="fixed left-[245px] right-0 top-0 z-10 flex h-[72px] items-center justify-between border-b border-[#d8d2c5] bg-[#f4f0e5]/95 px-8 backdrop-blur">
      
      <div className="flex items-center gap-3">
        <Sparkles size={16} className="text-[#314f43]" />

        <span className="text-[10px] font-medium uppercase tracking-[0.22em] text-[#58635d]">
          Online Merchant Intelligence
        </span>
      </div>

      <div className="flex items-center gap-7">
        <span className="hidden text-[10px] uppercase tracking-[0.18em] text-[#58635d] lg:block">
          Small businesses. Bigger possibilities.
        </span>

        <div className="h-8 w-px bg-[#d8d2c5]" />

        <button className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#1c2b26] text-sm text-white">
            S
          </div>

          <div className="hidden text-left sm:block">
            <p className="text-[12px] font-medium text-[#18231f]">
              Shivansh
            </p>

            <p className="text-[10px] text-[#7b847e]">
              Merchant
            </p>
          </div>

          <ChevronDown size={15} className="text-[#68736d]" />
        </button>
      </div>
    </header>
  );
}

export default Topbar;