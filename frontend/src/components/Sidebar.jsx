import {
  LayoutDashboard,
  BarChart3,
  Sparkles,
  Tag,
  FlaskConical,
  CreditCard,
  Activity,
  Settings,
} from "lucide-react";

const navigation = [
  { name: "Overview", icon: LayoutDashboard },
  { name: "Analytics", icon: BarChart3 },
  { name: "AI Growth", icon: Sparkles },
  { name: "Offers", icon: Tag },
  { name: "Experiments", icon: FlaskConical },
  { name: "Checkout", icon: CreditCard },
  { name: "AI Activity", icon: Activity },
];

function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-20 flex h-screen w-[245px] flex-col border-r border-[#39463f] bg-[#13201c] text-[#f4f0e5]">
      
      {/* Brand */}
      <div className="border-b border-[#39463f] px-7 py-7">
        <h1 className="font-['Space_Mono'] text-[23px] font-bold tracking-tight">
          ShopControl
        </h1>

        <p className="mt-2 text-[11px] uppercase tracking-[0.18em] text-[#aab6ad]">
          AI That Sells For You
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-5">
        {navigation.map((item, index) => {
          const Icon = item.icon;
          const active = index === 0;

          return (
            <button
              key={item.name}
              className={`group mb-1 flex w-full items-center gap-4 rounded-xl px-4 py-3 text-left text-[13px] transition-all ${
                active
                  ? "bg-[#31423a] text-[#ffffff]"
                  : "text-[#b9c2bc] hover:bg-[#26362f] hover:text-white"
              }`}
            >
              <Icon
                size={18}
                strokeWidth={1.7}
                className={active ? "text-[#b8d7c3]" : "text-[#a2afa7]"}
              />

              <span>{item.name}</span>
            </button>
          );
        })}
      </nav>

      {/* Bottom */}
      <div className="border-t border-[#39463f] px-5 py-5">
        <button className="mb-5 flex w-full items-center gap-4 rounded-xl px-3 py-3 text-[13px] text-[#b9c2bc] transition hover:bg-[#26362f] hover:text-white">
          <Settings size={18} strokeWidth={1.7} />
          Settings
        </button>

        <div className="rounded-xl border border-[#63736a] p-4">
          <p className="text-[10px] uppercase tracking-[0.2em] text-[#d8ded9]">
            Higher Revenue
          </p>

          <p className="mt-1 text-[10px] uppercase tracking-[0.2em] text-[#d8ded9]">
            Happier Merchants
          </p>
        </div>

        <p className="mt-5 text-[10px] text-[#65736c]">
          v1.0.0
        </p>
      </div>
    </aside>
  );
}

export default Sidebar;