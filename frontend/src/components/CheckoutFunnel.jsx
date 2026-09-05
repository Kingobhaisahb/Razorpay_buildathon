import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function CheckoutFunnel({ checkout }) {
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
    <div className="h-[280px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{
            top: 15,
            right: 10,
            left: -15,
            bottom: 5,
          }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#ddd8cd"
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
    </div>
  );
}

export default CheckoutFunnel;