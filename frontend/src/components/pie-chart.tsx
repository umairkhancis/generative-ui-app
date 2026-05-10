import { z } from "zod";

export const PieChartProps = z.object({
  title: z.string().optional().describe("Chart title"),
  slices: z
    .array(
      z.object({
        label: z.string().describe("Slice label"),
        value: z.number().describe("Slice value"),
      }),
    )
    .min(1)
    .describe("Slices of the pie, one per category"),
});

type PieChartProps = z.infer<typeof PieChartProps>;

const PALETTE = ["#1f2937", "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6"];

export function PieChart({ title, slices }: Partial<PieChartProps>) {
  if (!slices || slices.length === 0) return null;
  const total = slices.reduce((s, x) => s + (x?.value ?? 0), 0) || 1;
  const cx = 80;
  const cy = 80;
  const r = 70;
  let acc = 0;
  const paths = slices.map((slice, i) => {
    const start = (acc / total) * Math.PI * 2 - Math.PI / 2;
    acc += slice?.value ?? 0;
    const end = (acc / total) * Math.PI * 2 - Math.PI / 2;
    const large = end - start > Math.PI ? 1 : 0;
    const x1 = cx + r * Math.cos(start);
    const y1 = cy + r * Math.sin(start);
    const x2 = cx + r * Math.cos(end);
    const y2 = cy + r * Math.sin(end);
    const d = `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2} Z`;
    return <path key={i} d={d} fill={PALETTE[i % PALETTE.length]} />;
  });

  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm p-4 max-w-sm">
      {title && <div className="text-sm font-semibold text-gray-900 mb-3">{title}</div>}
      <div className="flex items-center gap-4">
        <svg width="160" height="160" viewBox="0 0 160 160">
          {paths}
        </svg>
        <ul className="flex-1 space-y-1.5">
          {slices.map((slice, i) => {
            const pct = (((slice?.value ?? 0) / total) * 100).toFixed(1);
            return (
              <li key={i} className="flex items-center text-xs text-gray-700">
                <span
                  className="inline-block w-3 h-3 rounded-sm mr-2"
                  style={{ backgroundColor: PALETTE[i % PALETTE.length] }}
                />
                <span className="flex-1 truncate">{slice.label}</span>
                <span className="ml-2 font-medium text-gray-900">{pct}%</span>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
