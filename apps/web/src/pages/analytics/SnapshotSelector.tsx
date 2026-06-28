import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import { api } from "../../lib/api";

interface Props {
  value: string;
  onChange: (id: string) => void;
}

export function SnapshotSelector({ value, onChange }: Props) {
  const { data } = useQuery({
    queryKey: ["snapshots"],
    queryFn: () => api.snapshots.list({ size: 20 }),
  });

  return (
    <div className="flex items-center gap-2">
      <label className="text-caption text-text-secondary whitespace-nowrap">
        Snapshot:
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-md border border-border bg-surface px-3 py-1.5 text-body text-text-primary focus:border-accent focus:outline-none"
      >
        <option value="">Select snapshot…</option>
        {data?.items?.map((s) => (
          <option key={s.id} value={s.id}>
            {format(new Date(s.reporting_date), "dd MMM yyyy")} — {s.status}
          </option>
        ))}
      </select>
    </div>
  );
}
