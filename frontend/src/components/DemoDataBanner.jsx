import { Database, X } from "lucide-react";
import { useState } from "react";

function DemoDataBanner() {
  const [open, setOpen] = useState(false);

  return (
    <div className="mb-5">

      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 rounded-full border border-[#d5a85b] bg-[#f8ecd2] px-3 py-2 text-[10px] font-bold uppercase tracking-[0.12em] text-[#78591f] transition hover:bg-[#f4e4c1]"
      >
        <Database size={13} />
        Demo Data
      </button>

      {open && (
        <div className="mt-3 rounded-2xl border border-[#d8c59d] bg-[#faf4e5] p-5">

          <div className="flex items-start justify-between">

            <div className="flex gap-3">

              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#ead9b5] text-[#78591f]">
                <Database size={17} />
              </div>

              <div>

                <h3 className="font-mono text-sm font-bold">
                  Demo Data Mode
                </h3>

                <p className="mt-1 max-w-2xl text-[11px] leading-5 text-[#75664a]">
                  You're currently viewing ShopControl using
                  simulated merchant data for demonstration.
                  The analytics and AI agents are processing this
                  dataset in real time.
                </p>

              </div>

            </div>

            <button
              onClick={() => setOpen(false)}
              className="text-[#806f51]"
            >
              <X size={16} />
            </button>

          </div>


          <div className="mt-5 grid grid-cols-2 gap-3 md:grid-cols-5">

            <DataPoint value="1" label="Merchant" />
            <DataPoint value="101" label="Products" />
            <DataPoint value="1,000" label="Customers" />
            <DataPoint value="5,000" label="Orders" />
            <DataPoint value="10,000" label="Checkouts" />

          </div>


          <div className="mt-4 border-t border-[#dfceb0] pt-4">

            <p className="text-[10px] uppercase tracking-[0.12em] text-[#8a7651]">
              Production architecture
            </p>

            <p className="mt-1 text-[11px] text-[#75664a]">
              In production, this data layer can be connected to
              live merchant commerce data and Razorpay transactions.
            </p>

          </div>

        </div>
      )}

    </div>
  );
}


function DataPoint({ value, label }) {
  return (
    <div className="rounded-xl border border-[#dfceb0] bg-[#f8f0dc] p-3">
      <p className="font-mono text-sm font-bold text-[#4c402b]">
        {value}
      </p>

      <p className="mt-1 text-[9px] uppercase tracking-wider text-[#887755]">
        {label}
      </p>
    </div>
  );
}


export default DemoDataBanner;