import { useEffect, useState } from "react";

import {
  Activity,
  BarChart3,
  BrainCircuit,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  CircleAlert,
  CreditCard,
  Database,
  FlaskConical,
  LayoutDashboard,
  Package,
  RefreshCw,
  ShieldCheck,
  ShoppingCart,
  Sparkles,
  Tag,
  TrendingDown,
  TrendingUp,
  WalletCards,
  XCircle,
} from "lucide-react";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  getAnalytics,
  getAIActions,
  getExperiments,
  getGrowth,
  getOffers,
} from "./services/api";

import DemoDataBanner from "./components/DemoDataBanner";


/* =========================================================
   NAVIGATION
========================================================= */

const navigation = [
  {
    id: "overview",
    name: "Overview",
    icon: LayoutDashboard,
  },
  {
    id: "analytics",
    name: "Analytics",
    icon: BarChart3,
  },
  {
    id: "growth",
    name: "AI Growth",
    icon: Sparkles,
  },
  {
    id: "offers",
    name: "Offers",
    icon: Tag,
  },
  {
    id: "experiments",
    name: "Experiments",
    icon: FlaskConical,
  },
  {
    id: "checkout",
    name: "Checkout",
    icon: CreditCard,
  },
  {
    id: "activity",
    name: "AI Activity",
    icon: Activity,
  },
];


/* =========================================================
   APP
========================================================= */

function App() {

  const [page, setPage] = useState("overview");

  const [analytics, setAnalytics] = useState(null);
  const [growth, setGrowth] = useState(null);
  const [offers, setOffers] = useState([]);
  const [experiments, setExperiments] = useState([]);
  const [actions, setActions] = useState([]);

  const [loading, setLoading] = useState(true);
  const [growthLoading, setGrowthLoading] = useState(false);
  const [error, setError] = useState("");


  /* =======================================================
     INITIAL DATA
  ======================================================= */

  useEffect(() => {
    loadDashboardData();
  }, []);


  const loadDashboardData = async () => {

    try {

      setLoading(true);
      setError("");

      const [
        analyticsData,
        offersData,
        experimentsData,
        actionsData,
      ] = await Promise.all([
        getAnalytics(),
        getOffers(),
        getExperiments(),
        getAIActions(),
      ]);

      setAnalytics(analyticsData);
      setOffers(offersData);
      setExperiments(experimentsData);
      setActions(actionsData);

    } catch (err) {

      console.error(err);

      setError(
        "Unable to connect to the ShopControl backend."
      );

    } finally {

      setLoading(false);

    }

  };


  /* =======================================================
     CHIEF GROWTH
  ======================================================= */

  const runGrowthAnalysis = async () => {

    try {

      setGrowthLoading(true);

      const result = await getGrowth();

      console.log(
        "Chief Growth Agent result:",
        result
      );

      setGrowth(result);

      setPage("growth");

    } catch (err) {

      console.error(
        "Chief Growth Agent error:",
        err
      );

      setError(
        "Chief Growth Agent could not complete the analysis."
      );

    } finally {

      setGrowthLoading(false);

    }

  };


  /* =======================================================
     LOADING
  ======================================================= */

  if (loading) {
    return <LoadingScreen />;
  }


  /* =======================================================
     ERROR
  ======================================================= */

  if (error && !analytics) {
    return (
      <ErrorScreen
        message={error}
        onRetry={loadDashboardData}
      />
    );
  }


  return (
    <div className="min-h-screen bg-[#f4f0e5] text-[#18231f]">

      <div className="flex min-h-screen">

        {/* =================================================
            SIDEBAR
        ================================================= */}

        <aside className="fixed left-0 top-0 z-30 hidden h-screen w-[245px] flex-col bg-[#13201c] text-[#f4f0e5] md:flex">

          {/* BRAND */}

          <div className="border-b border-[#39463f] px-7 py-7">

            <h1 className="font-mono text-2xl font-bold">
              ShopControl
            </h1>

            <p className="mt-2 text-[10px] uppercase tracking-[0.2em] text-[#aab6ad]">
              AI That Sells For You
            </p>

          </div>


          {/* NAVIGATION */}

          <nav className="flex-1 px-3 py-5">

            {navigation.map((item) => {

              const Icon = item.icon;

              const active =
                page === item.id;

              return (
                <button
                  key={item.id}
                  onClick={() => setPage(item.id)}
                  className={`mb-1 flex w-full items-center gap-4 rounded-xl px-4 py-3 text-left text-sm transition ${
                    active
                      ? "bg-[#31423a] text-white"
                      : "text-[#b9c2bc] hover:bg-[#26362f]"
                  }`}
                >

                  <Icon
                    size={17}
                    strokeWidth={1.7}
                    className={
                      active
                        ? "text-[#b8d7c3]"
                        : "text-[#91a097]"
                    }
                  />

                  {item.name}

                </button>
              );

            })}

          </nav>


          {/* BOTTOM */}

          <div className="border-t border-[#39463f] p-5">

            <button className="mb-5 flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm text-[#b9c2bc] hover:bg-[#26362f]">
              <span>⚙</span>
              Settings
            </button>


            <div className="rounded-xl border border-[#63736a] p-4">

              <p className="text-[10px] uppercase tracking-[0.2em]">
                Higher Revenue
              </p>

              <p className="mt-1 text-[10px] uppercase tracking-[0.2em]">
                Happier Merchants
              </p>

            </div>


            <p className="mt-5 text-[10px] text-[#65736c]">
              v1.0.0
            </p>

          </div>

        </aside>


        {/* =================================================
            MAIN
        ================================================= */}

        <main className="min-w-0 flex-1 md:ml-[245px]">


          {/* TOPBAR */}

          <header className="sticky top-0 z-20 flex h-[72px] items-center justify-between border-b border-[#d8d2c5] bg-[#f4f0e5]/95 px-6 backdrop-blur md:px-8">

            <div>

              <p className="text-[10px] uppercase tracking-[0.2em] text-[#58635d]">
                ✦ Online Merchant Intelligence
              </p>

            </div>


            <div className="flex items-center gap-3">

              <span className="hidden text-[10px] uppercase tracking-[0.15em] text-[#58635d] lg:block">
                Small businesses. Bigger possibilities.
              </span>

              <div className="h-8 w-px bg-[#d8d2c5]" />

              <div className="flex items-center gap-3">

                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#1c2b26] text-sm text-white">
                  S
                </div>

                <div className="hidden sm:block">

                  <p className="text-xs font-medium">
                    Shivansh
                  </p>

                  <p className="text-[10px] text-[#7b847e]">
                    Merchant
                  </p>

                </div>

              </div>

            </div>

          </header>


          {/* PAGE CONTENT */}

          <div className="mx-auto max-w-[1500px] px-6 py-8 md:px-8">

            {page === "overview" && (
              <OverviewPage
                analytics={analytics}
                offers={offers}
                experiments={experiments}
                onRunGrowth={runGrowthAnalysis}
                growthLoading={growthLoading}
                onRefresh={loadDashboardData}
              />
            )}


            {page === "analytics" && (
              <AnalyticsPage
                analytics={analytics}
              />
            )}


            {page === "growth" && (
              <GrowthPage
                growth={growth}
                loading={growthLoading}
                onRun={runGrowthAnalysis}
              />
            )}


            {page === "offers" && (
              <OffersPage
                offers={offers}
                analytics={analytics}
              />
            )}


            {page === "experiments" && (
              <ExperimentsPage
                experiments={experiments}
              />
            )}


            {page === "checkout" && (
              <CheckoutPage
                analytics={analytics}
              />
            )}


            {page === "activity" && (
              <ActivityPage
                actions={actions}
              />
            )}

          </div>

        </main>

      </div>

    </div>
  );
}


/* =========================================================
   OVERVIEW
========================================================= */

function OverviewPage({
  analytics,
  offers,
  experiments,
  onRunGrowth,
  growthLoading,
  onRefresh,
}) {

  const business = analytics.business;
  const checkout = analytics.checkout;
  const devices = analytics.device_performance;
  const payments = analytics.payment_method_performance;
  const products = analytics.product_performance || [];


  return (
    <>

      {/* HERO */}

      <PageHeader
        eyebrow="Merchant Dashboard"
        title="Welcome back, Shivansh"
        description="Here's what's happening with your store today."
        action={
          <button
            onClick={onRunGrowth}
            disabled={growthLoading}
            className="flex items-center gap-2 rounded-xl bg-[#17251f] px-5 py-3 text-xs font-medium text-white transition hover:bg-[#253a31] disabled:opacity-60"
          >

            {growthLoading ? (
              <RefreshCw
                size={14}
                className="animate-spin"
              />
            ) : (
              <BrainCircuit size={14} />
            )}

            Run AI Analysis

          </button>
        }
      />


      {/* DEMO DATA */}

      <DemoDataBanner />


      {/* KPI */}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <KPI
          title="Total Revenue"
          value={formatCurrency(
            business.revenue
          )}
          icon={<TrendingUp size={18} />}
        />

        <KPI
          title="Total Orders"
          value={business.orders.toLocaleString()}
          icon={<ShoppingCart size={18} />}
        />

        <KPI
          title="Average Order Value"
          value={formatCurrency(
            business.average_order_value
          )}
          icon={<WalletCards size={18} />}
        />

        <KPI
          title="Checkout Completion"
          value={`${checkout.completion_rate}%`}
          icon={<CheckCircle2 size={18} />}
        />

      </div>


      {/* FUNNEL + DEVICES */}

      <div className="mt-5 grid grid-cols-1 gap-5 lg:grid-cols-3">

        <Panel
          title="Checkout Funnel"
          className="lg:col-span-2"
        >

          <CheckoutChart
            checkout={checkout}
          />

        </Panel>


        <Panel title="Device Performance">

          <DeviceList
            devices={devices}
          />

        </Panel>

      </div>


      {/* PAYMENT + PRODUCTS */}

      <div className="mt-5 grid grid-cols-1 gap-5 lg:grid-cols-2">

        <Panel title="Payment Performance">

          <PaymentList
            payments={payments}
          />

        </Panel>


        <Panel title="Top Products">

          <ProductList
            products={products}
          />

        </Panel>

      </div>


      {/* AI + EXPERIMENT */}

      <div className="mt-5 grid grid-cols-1 gap-5 lg:grid-cols-2">

        <Panel title="AI Growth Intelligence">

          <MiniGrowthCard
            onRun={onRunGrowth}
            loading={growthLoading}
          />

        </Panel>


        <Panel title="Latest Experiment">

          {experiments.length > 0 ? (
            <ExperimentSummary
              experiment={experiments[0]}
            />
          ) : (
            <EmptyState
              icon={<FlaskConical size={20} />}
              text="No experiments found."
            />
          )}

        </Panel>

      </div>


      {/* REFRESH */}

      <div className="mt-5 flex justify-end">

        <button
          onClick={onRefresh}
          className="flex items-center gap-2 rounded-lg border border-[#d1cbbf] px-4 py-2 text-[10px] uppercase tracking-wider text-[#68736d] hover:bg-[#eeeae0]"
        >

          <RefreshCw size={13} />

          Refresh Store Data

        </button>

      </div>

    </>
  );
}


/* =========================================================
   ANALYTICS PAGE
========================================================= */

function AnalyticsPage({ analytics }) {

  const business = analytics.business;
  const checkout = analytics.checkout;
  const devices = analytics.device_performance;
  const payments = analytics.payment_method_performance;


  return (
    <>

      <PageHeader
        eyebrow="Commerce Intelligence"
        title="Analytics"
        description="A deterministic view of your store's performance."
      />


      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <KPI
          title="Revenue"
          value={formatCurrency(business.revenue)}
          icon={<TrendingUp size={18} />}
        />

        <KPI
          title="Orders"
          value={business.orders.toLocaleString()}
          icon={<ShoppingCart size={18} />}
        />

        <KPI
          title="AOV"
          value={formatCurrency(
            business.average_order_value
          )}
          icon={<WalletCards size={18} />}
        />

        <KPI
          title="Checkout Sessions"
          value={checkout.sessions.toLocaleString()}
          icon={<Activity size={18} />}
        />

      </div>


      <div className="mt-5 grid grid-cols-1 gap-5 lg:grid-cols-2">

        <Panel title="Checkout Performance">

          <MetricGrid
            items={[
              [
                "Completion",
                `${checkout.completion_rate}%`,
              ],
              [
                "Abandonment",
                `${checkout.abandonment_rate}%`,
              ],
              [
                "Failure",
                `${checkout.failure_rate}%`,
              ],
              [
                "Completed",
                checkout.completed.toLocaleString(),
              ],
            ]}
          />

        </Panel>


        <Panel title="Device Conversion">

          <DeviceList
            devices={devices}
          />

        </Panel>

      </div>


      <div className="mt-5">

        <Panel title="Payment Method Performance">

          <PaymentList
            payments={payments}
          />

        </Panel>

      </div>

    </>
  );
}


/* =========================================================
   AI GROWTH PAGE
========================================================= */

function GrowthPage({
  growth,
  loading,
  onRun,
}) {

  if (loading) {

    return (
      <PageShell
        eyebrow="Autonomous Growth"
        title="AI Growth"
        description="Chief Growth is consulting the specialized agents."
      >

        <div className="flex min-h-[400px] items-center justify-center">

          <div className="text-center">

            <BrainCircuit
              size={35}
              className="mx-auto animate-pulse text-[#315846]"
            />

            <p className="mt-5 font-mono text-sm font-bold">
              Chief Growth Agent is thinking...
            </p>

            <p className="mt-2 text-xs text-[#727b75]">
              Analyzing opportunities and financial safety.
            </p>

          </div>

        </div>

      </PageShell>
    );
  }


  if (!growth) {

    return (
      <PageShell
        eyebrow="Autonomous Growth"
        title="AI Growth"
        description="Your autonomous growth intelligence center."
      >

        <div className="rounded-2xl border border-[#d7d1c4] bg-[#f9f6ee] p-10 text-center">

          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-[#dceade] text-[#315846]">

            <Sparkles size={25} />

          </div>

          <h3 className="mt-5 font-mono text-xl font-bold">
            Find your next growth opportunity
          </h3>

          <p className="mx-auto mt-3 max-w-lg text-xs leading-6 text-[#6e7972]">
            Chief Growth coordinates the Offer Agent and
            Checkout Agent, prioritizes detected opportunities,
            and asks Gemini to produce a practical recommendation.
          </p>

          <button
            onClick={onRun}
            className="mt-6 rounded-xl bg-[#17251f] px-5 py-3 text-xs text-white"
          >
            Run Chief Growth Agent
          </button>

        </div>

      </PageShell>
    );
  }


  const recommendation =
    growth.recommendation || {};

  const opportunities =
    growth.opportunities || [];


  return (
    <PageShell
      eyebrow="Autonomous Growth"
      title="AI Growth"
      description="Chief Growth Agent coordinating your specialized growth agents."
    >

      {/* RECOMMENDATION */}

      <div className="rounded-2xl border border-[#c6d9ca] bg-[#dfeade] p-7">

        <div className="flex flex-col justify-between gap-5 md:flex-row">

          <div className="flex gap-3">

            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#c5ddca]">

              <Sparkles
                size={19}
                className="text-[#315846]"
              />

            </div>

            <div>

              <p className="text-[10px] uppercase tracking-[0.16em] text-[#52675b]">
                Chief Growth Agent
              </p>

              <p className="mt-1 text-[9px] text-[#718078]">
                Deterministic analytics + specialized agents + Gemini reasoning
              </p>

            </div>

          </div>


          <div className="flex gap-2">

            <Badge
              text={`${recommendation.priority || "HIGH"} PRIORITY`}
            />

            <Badge
              text={`${Math.round(
                (recommendation.confidence || 0) * 100
              )}% CONFIDENCE`}
            />

          </div>

        </div>


        <h2 className="mt-7 max-w-4xl font-mono text-2xl font-bold leading-9">
          {recommendation.top_opportunity ||
            "Growth opportunity identified"}
        </h2>


        <div className="mt-5 max-w-4xl">

          <p className="text-xs leading-7 text-[#53645a]">
            {recommendation.reasoning ||
              recommendation.business_summary}
          </p>

        </div>


        <div className="mt-6 rounded-xl border border-[#c7dacb] bg-[#e9f0e7] p-5">

          <p className="text-[9px] uppercase tracking-[0.14em] text-[#718078]">
            Recommended Action
          </p>

          <p className="mt-2 font-mono text-sm font-bold">
            {recommendation.recommended_action}
          </p>

        </div>


        <div className="mt-5 flex flex-wrap items-center gap-3">

          {recommendation.requires_approval ? (

            <div className="flex items-center gap-2 rounded-lg border border-[#c4d6c7] px-4 py-2.5 text-[10px] text-[#52645a]">

              <ShieldCheck size={14} />

              Merchant approval required

            </div>

          ) : (

            <div className="flex items-center gap-2 rounded-lg bg-[#17251f] px-4 py-2.5 text-[10px] text-white">

              <CheckCircle2 size={14} />

              Eligible for automation

            </div>

          )}


          <button
            onClick={onRun}
            className="flex items-center gap-2 rounded-lg bg-[#17251f] px-4 py-2.5 text-xs text-white"
          >

            <RefreshCw size={13} />

            Re-run Analysis

          </button>

        </div>

      </div>


      {/* OPPORTUNITIES */}

      <div className="mt-5">

        <Panel title={`Detected Opportunities · ${opportunities.length}`}>

          <div className="space-y-3">

            {opportunities.map(
              (opportunity, index) => (

                <Opportunity
                  key={index}
                  opportunity={opportunity}
                  rank={index + 1}
                />

              )
            )}

          </div>

        </Panel>

      </div>

    </PageShell>
  );
}


/* =========================================================
   OFFERS PAGE
========================================================= */

function OffersPage({
  offers,
  analytics,
}) {

  const products =
    analytics?.product_performance || [];


  return (
    <PageShell
      eyebrow="Offer Intelligence"
      title="Offers"
      description="Offer Agent recommendations and merchant offer configuration."
    >

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">

        <KPI
          title="Configured Offers"
          value={offers.length}
          icon={<Tag size={18} />}
        />

        <KPI
          title="Active Offers"
          value={
            offers.filter(
              (offer) => offer.active
            ).length
          }
          icon={<CheckCircle2 size={18} />}
        />

        <KPI
          title="Products Analyzed"
          value={products.length}
          icon={<Package size={18} />}
        />

      </div>


      <div className="mt-5">

        <Panel title="Merchant Offers">

          {offers.length === 0 ? (

            <EmptyState
              icon={<Tag size={20} />}
              text="No offers configured."
            />

          ) : (

            <div className="overflow-x-auto">

              <table className="w-full text-left">

                <thead>

                  <tr className="border-b border-[#e0dbd0] text-[9px] uppercase tracking-wider text-[#7a837d]">

                    <th className="pb-3">
                      Offer
                    </th>

                    <th className="pb-3">
                      Discount
                    </th>

                    <th className="pb-3">
                      Max Discount
                    </th>

                    <th className="pb-3">
                      Min Margin
                    </th>

                    <th className="pb-3">
                      Budget
                    </th>

                    <th className="pb-3">
                      Status
                    </th>

                  </tr>

                </thead>


                <tbody>

                  {offers.map((offer) => (

                    <tr
                      key={offer.id}
                      className="border-b border-[#e8e3d9] last:border-0"
                    >

                      <td className="py-4 text-xs font-medium">
                        {offer.name}
                      </td>

                      <td className="py-4 font-mono text-xs">
                        {offer.discount_percent}%
                      </td>

                      <td className="py-4 font-mono text-xs">
                        {offer.max_discount_percent}%
                      </td>

                      <td className="py-4 font-mono text-xs">
                        {offer.min_margin_percent}%
                      </td>

                      <td className="py-4 font-mono text-xs">
                        {formatCurrency(
                          offer.budget
                        )}
                      </td>

                      <td className="py-4">

                        <StatusBadge
                          active={offer.active}
                        />

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          )}

        </Panel>

      </div>

    </PageShell>
  );
}


/* =========================================================
   EXPERIMENTS PAGE
========================================================= */

function ExperimentsPage({
  experiments,
}) {

  return (
    <PageShell
      eyebrow="Experimentation"
      title="Experiments"
      description="A/B testing and statistical decision intelligence."
    >

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">

        <KPI
          title="Experiments"
          value={experiments.length}
          icon={<FlaskConical size={18} />}
        />

        <KPI
          title="Significant"
          value={
            experiments.filter(
              (experiment) =>
                experiment.statistically_significant
            ).length
          }
          icon={<CheckCircle2 size={18} />}
        />

        <KPI
          title="Completed"
          value={
            experiments.filter(
              (experiment) =>
                experiment.status === "completed"
            ).length
          }
          icon={<Activity size={18} />}
        />

      </div>


      <div className="mt-5 space-y-5">

        {experiments.map((experiment) => (

          <Panel
            key={experiment.id}
            title={`Experiment #${experiment.id}`}
          >

            <ExperimentDetail
              experiment={experiment}
            />

          </Panel>

        ))}

      </div>

    </PageShell>
  );
}


/* =========================================================
   CHECKOUT PAGE
========================================================= */

function CheckoutPage({ analytics }) {

  const checkout = analytics.checkout;
  const devices = analytics.device_performance;
  const payments = analytics.payment_method_performance;


  return (
    <PageShell
      eyebrow="Checkout Intelligence"
      title="Checkout"
      description="Understand where customers drop before completing payment."
    >

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <KPI
          title="Sessions"
          value={checkout.sessions.toLocaleString()}
          icon={<Activity size={18} />}
        />

        <KPI
          title="Completed"
          value={checkout.completed.toLocaleString()}
          icon={<CheckCircle2 size={18} />}
        />

        <KPI
          title="Abandoned"
          value={checkout.abandoned.toLocaleString()}
          icon={<TrendingDown size={18} />}
        />

        <KPI
          title="Failed"
          value={checkout.failed.toLocaleString()}
          icon={<XCircle size={18} />}
        />

      </div>


      <div className="mt-5 grid grid-cols-1 gap-5 lg:grid-cols-2">

        <Panel title="Checkout Funnel">

          <CheckoutChart
            checkout={checkout}
          />

        </Panel>


        <Panel title="Device Performance">

          <DeviceList
            devices={devices}
          />

        </Panel>

      </div>


      <div className="mt-5">

        <Panel title="Payment Methods">

          <PaymentList
            payments={payments}
          />

        </Panel>

      </div>

    </PageShell>
  );
}


/* =========================================================
   AI ACTIVITY PAGE
========================================================= */

function ActivityPage({ actions }) {

  return (
    <PageShell
      eyebrow="Agent Operations"
      title="AI Activity"
      description="Auditable activity generated by ShopControl's AI agents."
    >

      <div className="rounded-2xl border border-[#d7d1c4] bg-[#f9f6ee]">

        {actions.length === 0 ? (

          <div className="p-10">

            <EmptyState
              icon={<Activity size={20} />}
              text="No AI actions recorded."
            />

          </div>

        ) : (

          <div>

            {actions.map((action) => (

              <div
                key={action.id}
                className="flex flex-col gap-4 border-b border-[#e0dbd0] p-5 last:border-0 md:flex-row md:items-center md:justify-between"
              >

                <div className="flex gap-4">

                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#dceade] text-[#315846]">

                    {action.agent_name
                      ?.toLowerCase()
                      .includes("offer") ? (
                      <Tag size={17} />
                    ) : (
                      <BrainCircuit size={17} />
                    )}

                  </div>


                  <div>

                    <div className="flex flex-wrap items-center gap-2">

                      <p className="text-xs font-bold">
                        {action.agent_name}
                      </p>

                      <span className="text-[9px] text-[#8a928c]">
                        #{action.id}
                      </span>

                    </div>


                    <p className="mt-1 max-w-2xl text-[11px] leading-5 text-[#68736d]">
                      {action.description}
                    </p>


                    <p className="mt-2 text-[9px] uppercase tracking-wider text-[#929a94]">
                      {action.action_type}
                    </p>

                  </div>

                </div>


                <div className="flex shrink-0 items-center gap-4">

                  <StatusPill
                    status={action.status}
                  />

                  <span className="text-[9px] text-[#89928b]">
                    {formatDate(action.created_at)}
                  </span>

                </div>

              </div>

            ))}

          </div>

        )}

      </div>

    </PageShell>
  );
}


/* =========================================================
   SHARED COMPONENTS
========================================================= */

function PageHeader({
  eyebrow,
  title,
  description,
  action,
}) {

  return (
    <div className="mb-8 flex flex-col justify-between gap-5 lg:flex-row lg:items-end">

      <div>

        <p className="mb-2 text-[10px] uppercase tracking-[0.2em] text-[#758078]">
          {eyebrow}
        </p>

        <h2 className="font-mono text-3xl font-bold tracking-tight md:text-4xl">
          {title}
        </h2>

        <p className="mt-2 text-sm text-[#68736d]">
          {description}
        </p>

      </div>


      {action}

    </div>
  );
}


function PageShell({
  eyebrow,
  title,
  description,
  children,
}) {

  return (
    <>

      <PageHeader
        eyebrow={eyebrow}
        title={title}
        description={description}
      />

      {children}

    </>
  );
}


function KPI({
  title,
  value,
  icon,
}) {

  return (
    <div className="rounded-2xl border border-[#d7d1c4] bg-[#f9f6ee] p-5 transition hover:-translate-y-0.5 hover:shadow-lg">

      <div className="flex items-start justify-between">

        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#dceade] text-[#315846]">
          {icon}
        </div>

        <span className="text-[9px] uppercase tracking-wider text-[#47745a]">
          Live
        </span>

      </div>


      <p className="mt-5 text-[10px] uppercase tracking-[0.1em] text-[#727b75]">
        {title}
      </p>


      <p className="mt-1 font-mono text-2xl font-bold tracking-tight">
        {value}
      </p>

    </div>
  );
}


function Panel({
  title,
  children,
  className = "",
}) {

  return (
    <div
      className={`rounded-2xl border border-[#d7d1c4] bg-[#f9f6ee] p-5 ${className}`}
    >

      <div className="mb-5 flex items-center justify-between border-b border-[#e0dbd0] pb-4">

        <h3 className="font-mono text-sm font-bold">
          {title}
        </h3>

        <span className="text-lg text-[#6d7770]">
          ···
        </span>

      </div>

      {children}

    </div>
  );
}


/* =========================================================
   CHARTS
========================================================= */

function CheckoutChart({
  checkout,
}) {

  const data = [
    {
      name: "Sessions",
      value: checkout.sessions,
    },
    {
      name: "Completed",
      value: checkout.completed,
    },
    {
      name: "Abandoned",
      value: checkout.abandoned,
    },
    {
      name: "Failed",
      value: checkout.failed,
    },
  ];


  return (
    <div className="h-[300px]">

      <ResponsiveContainer
        width="100%"
        height="100%"
      >

        <BarChart
          data={data}
          margin={{
            top: 10,
            right: 10,
            left: -15,
            bottom: 5,
          }}
        >

          <CartesianGrid
            stroke="#ddd8cd"
            strokeDasharray="3 3"
            vertical={false}
          />

          <XAxis
            dataKey="name"
            tick={{
              fontSize: 10,
              fill: "#68736d",
            }}
            axisLine={false}
            tickLine={false}
          />

          <YAxis
            tick={{
              fontSize: 9,
              fill: "#68736d",
            }}
            axisLine={false}
            tickLine={false}
          />

          <Tooltip
            contentStyle={{
              background: "#f9f6ee",
              border: "1px solid #d7d1c4",
              borderRadius: "10px",
              fontSize: "11px",
            }}
            formatter={(value) => [
              Number(value).toLocaleString(),
              "Sessions",
            ]}
          />

          <Bar
            dataKey="value"
            fill="#6e9c82"
            radius={[6, 6, 0, 0]}
            maxBarSize={65}
          />

        </BarChart>

      </ResponsiveContainer>


      <div className="grid grid-cols-3 border-t border-[#e0dbd0] pt-4">

        <MiniStat
          label="Completion"
          value={`${checkout.completion_rate}%`}
        />

        <MiniStat
          label="Abandonment"
          value={`${checkout.abandonment_rate}%`}
        />

        <MiniStat
          label="Failure"
          value={`${checkout.failure_rate}%`}
        />

      </div>

    </div>
  );
}


/* =========================================================
   DEVICES
========================================================= */

function DeviceList({
  devices,
}) {

  const rows = [
    [
      "Desktop",
      devices.desktop,
    ],
    [
      "Mobile",
      devices.mobile,
    ],
    [
      "Tablet",
      devices.tablet,
    ],
  ];


  return (
    <div className="space-y-7">

      {rows.map(([name, data]) => {

        const value =
          Number(
            data?.conversion_rate || 0
          );

        return (
          <div key={name}>

            <div className="mb-2 flex justify-between text-xs">

              <span>{name}</span>

              <span className="font-mono font-bold">
                {value}%
              </span>

            </div>


            <div className="h-2 overflow-hidden rounded-full bg-[#e3dfd5]">

              <div
                className="h-full rounded-full bg-[#76a98b]"
                style={{
                  width: `${Math.min(
                    value,
                    100
                  )}%`,
                }}
              />

            </div>

          </div>
        );

      })}

    </div>
  );
}


/* =========================================================
   PAYMENTS
========================================================= */

function PaymentList({
  payments,
}) {

  const methods = [
    ["Card", payments.card],
    ["UPI", payments.upi],
    ["Wallet", payments.wallet],
    ["Netbanking", payments.netbanking],
  ];


  return (
    <div className="space-y-5">

      {methods.map(([name, data]) => {

        const failure =
          Number(
            data?.failure_rate || 0
          );

        const success =
          Number(
            data?.success_rate || 0
          );


        return (
          <div key={name}>

            <div className="flex items-center justify-between">

              <div className="flex items-center gap-3">

                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#dceade] text-[#315846]">

                  <CreditCard size={15} />

                </div>

                <span className="text-xs font-medium">
                  {name}
                </span>

              </div>


              <div className="text-right">

                <p className="font-mono text-xs font-bold">
                  {success}%
                </p>

                <p className="text-[9px] text-[#8a928c]">
                  success
                </p>

              </div>

            </div>


            <div className="mt-3 h-2 overflow-hidden rounded-full bg-[#e3dfd5]">

              <div
                className="h-full rounded-full bg-[#76a98b]"
                style={{
                  width: `${Math.min(
                    success,
                    100
                  )}%`,
                }}
              />

            </div>


            <p className="mt-1 text-[9px] text-[#8a928c]">
              {data?.payment_attempts?.toLocaleString?.() || 0} attempts · {failure}% failed
            </p>

          </div>
        );

      })}

    </div>
  );
}


/* =========================================================
   PRODUCTS
========================================================= */

function ProductList({
  products,
}) {

  const topProducts = products
    .slice()
    .sort(
      (a, b) =>
        Number(b.revenue || 0) -
        Number(a.revenue || 0)
    )
    .slice(0, 5);


  return (
    <div className="overflow-x-auto">

      <table className="w-full text-left">

        <thead>

          <tr className="border-b border-[#e0dbd0] text-[9px] uppercase tracking-wider text-[#7a837d]">

            <th className="pb-3">
              Product
            </th>

            <th className="pb-3 text-right">
              Revenue
            </th>

            <th className="pb-3 text-right">
              Margin
            </th>

          </tr>

        </thead>


        <tbody>

          {topProducts.map((product) => (

            <tr
              key={product.product_id}
              className="border-b border-[#e8e3d9] last:border-0"
            >

              <td className="py-3">

                <p className="max-w-[220px] truncate text-[11px] font-medium">
                  {product.product_name}
                </p>

                <p className="mt-1 text-[9px] text-[#8a928c]">
                  {product.category}
                </p>

              </td>


              <td className="py-3 text-right font-mono text-[10px] font-bold">
                {formatCurrency(
                  product.revenue
                )}
              </td>


              <td className="py-3 text-right">

                <span className="rounded-full bg-[#dceade] px-2 py-1 text-[9px] text-[#347457]">
                  {product.margin_percent}%
                </span>

              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
}


/* =========================================================
   GROWTH MINI CARD
========================================================= */

function MiniGrowthCard({
  onRun,
  loading,
}) {

  return (
    <div className="rounded-xl bg-[#dfeade] p-5">

      <div className="flex items-center gap-2">

        <Sparkles
          size={17}
          className="text-[#315846]"
        />

        <p className="text-[10px] uppercase tracking-[0.15em] text-[#52675b]">
          Chief Growth Agent
        </p>

      </div>


      <h3 className="mt-4 font-mono text-xl font-bold">
        Find your next revenue opportunity.
      </h3>


      <p className="mt-3 text-xs leading-6 text-[#53645a]">
        Chief Growth coordinates specialized agents,
        prioritizes opportunities and reasons about the
        safest high-impact action.
      </p>


      <button
        onClick={onRun}
        disabled={loading}
        className="mt-5 flex items-center gap-2 rounded-lg bg-[#17251f] px-4 py-2.5 text-xs text-white disabled:opacity-60"
      >

        {loading ? (
          <RefreshCw
            size={13}
            className="animate-spin"
          />
        ) : (
          <BrainCircuit size={13} />
        )}

        Run AI Analysis

      </button>

    </div>
  );
}


/* =========================================================
   OPPORTUNITY
========================================================= */

function Opportunity({
  opportunity,
  rank,
}) {

  return (
    <div className="rounded-xl border border-[#e0dbd0] p-4">

      <div className="flex gap-4">

        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#dceade] font-mono text-xs font-bold text-[#315846]">
          {rank}
        </div>


        <div className="min-w-0 flex-1">

          <div className="flex flex-wrap items-center gap-2">

            <p className="text-xs font-bold">
              {opportunity.recommended_action}
            </p>

            <span className="rounded-full bg-[#eeeae0] px-2 py-1 text-[8px] uppercase tracking-wider">
              {opportunity.source_agent}
            </span>

          </div>


          <p className="mt-2 text-[10px] leading-5 text-[#707a73]">
            {opportunity.hypothesis ||
              opportunity.evidence}
          </p>


          <div className="mt-3 flex flex-wrap gap-2">

            <Badge
              text={`${opportunity.severity || "medium"} severity`}
            />

            <Badge
              text={`score ${opportunity.priority_score ?? opportunity.score ?? 0}`}
            />

          </div>

        </div>

      </div>

    </div>
  );
}


/* =========================================================
   EXPERIMENTS
========================================================= */

function ExperimentSummary({
  experiment,
}) {

  return (
    <div>

      <div className="flex items-start justify-between gap-4">

        <div>

          <p className="text-sm font-bold">
            {experiment.name}
          </p>

          <p className="mt-1 text-[10px] leading-5 text-[#7a837d]">
            {experiment.hypothesis}
          </p>

        </div>

        <StatusPill
          status={experiment.status}
        />

      </div>


      <div className="mt-6 grid grid-cols-3 gap-3">

        <MetricBox
          label="Lift"
          value={`${experiment.conversion_lift}%`}
        />

        <MetricBox
          label="P-value"
          value={experiment.p_value}
        />

        <MetricBox
          label="Winner"
          value={
            experiment.winner || "—"
          }
        />

      </div>

    </div>
  );
}


function ExperimentDetail({
  experiment,
}) {

  return (
    <div>

      <div className="flex flex-col justify-between gap-4 md:flex-row">

        <div>

          <h3 className="font-mono text-lg font-bold">
            {experiment.name}
          </h3>

          <p className="mt-2 max-w-2xl text-xs leading-6 text-[#6e7972]">
            {experiment.hypothesis}
          </p>

        </div>


        <StatusPill
          status={experiment.status}
        />

      </div>


      <div className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-5">

        <MetricBox
          label="Control visitors"
          value={experiment.control_visitors?.toLocaleString()}
        />

        <MetricBox
          label="Variant visitors"
          value={experiment.variant_visitors?.toLocaleString()}
        />

        <MetricBox
          label="Control CVR"
          value={`${experiment.control_conversion}%`}
        />

        <MetricBox
          label="Variant CVR"
          value={`${experiment.variant_conversion}%`}
        />

        <MetricBox
          label="Conversion lift"
          value={`${experiment.conversion_lift}%`}
        />

      </div>


      <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-4">

        <MetricBox
          label="P-value"
          value={experiment.p_value}
        />

        <MetricBox
          label="Significance"
          value={
            experiment.statistically_significant
              ? "Significant"
              : "Not significant"
          }
        />

        <MetricBox
          label="Winner"
          value={experiment.winner || "—"}
        />

        <MetricBox
          label="Revenue lift"
          value={`${experiment.revenue_lift}%`}
        />

      </div>

    </div>
  );
}


/* =========================================================
   SMALL COMPONENTS
========================================================= */

function MetricGrid({
  items,
}) {

  return (
    <div className="grid grid-cols-2 gap-3">

      {items.map(([label, value]) => (

        <MetricBox
          key={label}
          label={label}
          value={value}
        />

      ))}

    </div>
  );
}


function MetricBox({
  label,
  value,
}) {

  return (
    <div className="rounded-xl border border-[#e0dbd0] bg-[#f5f1e8] p-4">

      <p className="text-[9px] uppercase tracking-wider text-[#7a837d]">
        {label}
      </p>

      <p className="mt-1 font-mono text-sm font-bold">
        {value ?? "—"}
      </p>

    </div>
  );
}


function MiniStat({
  label,
  value,
}) {

  return (
    <div className="text-center">

      <p className="text-[9px] uppercase tracking-wider text-[#7a837d]">
        {label}
      </p>

      <p className="mt-1 font-mono text-sm font-bold">
        {value}
      </p>

    </div>
  );
}


function Badge({
  text,
}) {

  return (
    <span className="rounded-full bg-[#cfe1d2] px-2.5 py-1 text-[8px] font-bold uppercase tracking-wider text-[#315846]">
      {text}
    </span>
  );
}


function StatusBadge({
  active,
}) {

  return (
    <span
      className={`rounded-full px-3 py-1 text-[9px] font-medium ${
        active
          ? "bg-[#dceade] text-[#347457]"
          : "bg-[#eeeae0] text-[#737d76]"
      }`}
    >
      {active ? "Active" : "Inactive"}
    </span>
  );
}


function StatusPill({
  status,
}) {

  const normalized =
    String(status || "unknown")
      .toLowerCase();


  const active =
    normalized === "completed" ||
    normalized === "ready" ||
    normalized === "approved";


  return (
    <span
      className={`rounded-full px-3 py-1 text-[9px] font-medium ${
        active
          ? "bg-[#dceade] text-[#347457]"
          : normalized.includes("approval")
          ? "bg-[#f8ecd2] text-[#78591f]"
          : "bg-[#eeeae0] text-[#737d76]"
      }`}
    >
      {status || "Unknown"}
    </span>
  );
}


function EmptyState({
  icon,
  text,
}) {

  return (
    <div className="flex flex-col items-center justify-center py-10 text-center">

      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#eeeae0] text-[#707a73]">
        {icon}
      </div>

      <p className="mt-3 text-xs text-[#737d76]">
        {text}
      </p>

    </div>
  );
}


/* =========================================================
   LOADING / ERROR
========================================================= */

function LoadingScreen() {

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#f4f0e5]">

      <div className="text-center">

        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-[#dceade]">

          <BrainCircuit
            size={25}
            className="animate-pulse text-[#315846]"
          />

        </div>

        <p className="mt-5 font-mono text-sm font-bold">
          Loading ShopControl
        </p>

        <p className="mt-2 text-[10px] uppercase tracking-[0.15em] text-[#7a837d]">
          Connecting to intelligence engine
        </p>

      </div>

    </div>
  );
}


function ErrorScreen({
  message,
  onRetry,
}) {

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#f4f0e5]">

      <div className="max-w-md rounded-2xl border border-[#d7d1c4] bg-[#f9f6ee] p-8 text-center">

        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-[#f5ded6] text-[#a34d38]">
          <CircleAlert size={22} />
        </div>

        <h2 className="mt-5 font-mono text-lg font-bold">
          Backend connection failed
        </h2>

        <p className="mt-2 text-xs text-[#737d76]">
          {message}
        </p>

        <button
          onClick={onRetry}
          className="mt-6 rounded-xl bg-[#17251f] px-5 py-3 text-xs text-white"
        >
          Try Again
        </button>

      </div>

    </div>
  );
}


/* =========================================================
   HELPERS
========================================================= */

function formatCurrency(value) {

  return new Intl.NumberFormat(
    "en-IN",
    {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 2,
    }
  ).format(Number(value || 0));
}


function formatDate(value) {

  if (!value) {
    return "Unknown";
  }

  try {

    return new Date(value).toLocaleString(
      "en-IN",
      {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      }
    );

  } catch {

    return "Unknown";

  }
}


export default App;