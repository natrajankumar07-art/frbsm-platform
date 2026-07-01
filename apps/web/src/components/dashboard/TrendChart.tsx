import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { format } from "date-fns";

export interface TrendDataPoint {
  date: string;
  lcr?: number;
  nsfr?: number;
  cet1?: number;
  leverage?: number;
  totalAssets?: number;
  hqla?: number;
}

interface TrendChartProps {
  data: TrendDataPoint[];
  title?: string;
  metrics?: ("lcr" | "nsfr" | "cet1" | "leverage")[];
}

const METRIC_CONFIG: Record<
  string,
  { color: string; label: string; formatter: (v: number) => string }
> = {
  lcr: { color: "#2B5BD7", label: "LCR", formatter: (v) => `${(v * 100).toFixed(1)}%` },
  nsfr: { color: "#1F7A4A", label: "NSFR", formatter: (v) => `${(v * 100).toFixed(1)}%` },
  cet1: { color: "#B8730F", label: "CET1", formatter: (v) => `${(v * 100).toFixed(1)}%` },
  leverage: { color: "#8B5CF6", label: "Leverage", formatter: (v) => `${(v * 100).toFixed(1)}%` },
};

function formatDate(dateStr: string): string {
  try {
    return format(new Date(dateStr), "dd MMM");
  } catch {
    return dateStr;
  }
}

export function TrendChart({
  data,
  title = "Regulatory Trends",
  metrics = ["lcr", "nsfr", "cet1"],
}: TrendChartProps) {
  const chartData = data.map((d) => ({
    ...d,
    displayDate: formatDate(d.date),
    lcr: d.lcr !== undefined ? +(d.lcr * 100).toFixed(2) : undefined,
    nsfr: d.nsfr !== undefined ? +(d.nsfr * 100).toFixed(2) : undefined,
    cet1: d.cet1 !== undefined ? +(d.cet1 * 100).toFixed(2) : undefined,
    leverage: d.leverage !== undefined ? +(d.leverage * 100).toFixed(2) : undefined,
  }));

  return (
    <div
      className="card dark:bg-gray-900 dark:border-gray-700"
      data-testid="trend-chart"
    >
      <h3 className="text-body font-semibold text-text-primary dark:text-gray-100 mb-4">
        {title}
      </h3>
      {data.length === 0 ? (
        <p className="text-body text-text-secondary dark:text-gray-400 text-center py-8">
          Multiple snapshots required for trend analysis.
        </p>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E6E4DE" />
            <XAxis
              dataKey="displayDate"
              tick={{ fontSize: 10, fill: "#5A6270" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 10, fill: "#5A6270" }}
              axisLine={false}
              tickLine={false}
              unit="%"
              width={36}
            />
            <Tooltip
              formatter={(value: number, name: string) => [
                `${value.toFixed(2)}%`,
                METRIC_CONFIG[name]?.label ?? name,
              ]}
              contentStyle={{
                backgroundColor: "#FFFFFF",
                border: "1px solid #E6E4DE",
                borderRadius: "6px",
                fontSize: "11px",
              }}
            />
            <Legend
              wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }}
              formatter={(value) => METRIC_CONFIG[value]?.label ?? value}
            />
            {metrics.map((m) => (
              <Line
                key={m}
                type="monotone"
                dataKey={m}
                stroke={METRIC_CONFIG[m].color}
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
                connectNulls
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
