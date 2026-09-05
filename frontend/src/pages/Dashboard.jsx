import {
  CalendarDays,
  Play,
  IndianRupee,
  ShoppingCart,
  BarChart3,
  TrendingUp,
} from "lucide-react";

import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import StatCard from "../components/StatCard";

function Dashboard() {
  return (
    <div className="min-h-screen bg-[#f4f0e5] text-[#18231f]">

      <Sidebar />
      <Topbar />

      <main className="ml-[245px] pt-[72px]">

        <div className="mx-auto max-w-[1500px] px-8 py-8">

          {/* Hero */}
          <section className="mb-8 flex items-end justify-between">
            <div>
              <p className="mb-2 text-[10px] uppercase tracking-[0.2em] text-[#758078]">
                Merchant Dashboard
              </p>

              <h2 className="font-['Space_Mono'] text-[32px] font-bold tracking-tight text-[#18231f]">
                Welcome back, Shivansh
              </h2>

              <p className="mt-2 text-[13px] text-[#68736d]">
                Here's what's happening with your store today.
              </p>
            </div>

            <div className="flex items-center gap-3">

              <button className="hidden items-center gap-3 rounded-xl border border-[#d1cbbf] bg-[#faf7ef] px-4 py-3 text-left sm:flex">
                <CalendarDays size={17} />

                <div>
                  <p className="text-[11px] font-medium">
                    Sat, 5 Sep 2026
                  </p>

                  <p className="text-[9px] text-[#7b847e]">
                    Today's performance
                  </p>
                </div>
              </button>

              <button className="flex items-center gap-2 rounded-xl bg-[#17251f] px-5 py-3 text-[11px] font-medium text-white transition hover:bg-[#253a31]">
                <Play size={14} fill="currentColor" />
                Run AI Analysis
              </button>

            </div>
          </section>

          {/* KPI Cards */}
          <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">

            <StatCard
              icon={IndianRupee}
              label="Total Revenue"
              value="₹10,07,09,060"
              change="+12.5%"
            />

            <StatCard
              icon={ShoppingCart}
              label="Total Orders"
              value="5,000"
              change="+8.3%"
            />

            <StatCard
              icon={BarChart3}
              label="Average Order Value"
              value="₹20,141.81"
              change="+4.2%"
            />

            <StatCard
              icon={TrendingUp}
              label="Checkout Completion"
              value="71.47%"
              change="+2.1%"
            />

          </section>

          {/* Placeholder */}
          <section className="mt-5 grid grid-cols-1 gap-5 lg:grid-cols-2">

            <div className="flex min-h-[300px] items-center justify-center rounded-2xl border border-dashed border-[#c9c2b5] bg-[#f8f5ed]">
              <div className="text-center">
                <BarChart3
                  size={30}
                  className="mx-auto mb-3 text-[#718078]"
                />

                <p className="font-['Space_Mono'] text-sm font-bold">
                  Checkout Analytics
                </p>

                <p className="mt-1 text-[11px] text-[#7c857f]">
                  Chart coming next
                </p>
              </div>
            </div>

            <div className="flex min-h-[300px] items-center justify-center rounded-2xl border border-dashed border-[#c9c2b5] bg-[#f8f5ed]">
              <div className="text-center">
                <TrendingUp
                  size={30}
                  className="mx-auto mb-3 text-[#718078]"
                />

                <p className="font-['Space_Mono'] text-sm font-bold">
                  AI Growth Intelligence
                </p>

                <p className="mt-1 text-[11px] text-[#7c857f]">
                  AI recommendation coming next
                </p>
              </div>
            </div>

          </section>

        </div>

      </main>
    </div>
  );
}

export default Dashboard;