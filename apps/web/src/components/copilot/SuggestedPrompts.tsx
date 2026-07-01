import { useQuery } from "@tanstack/react-query";
import { clsx } from "clsx";

interface SuggestedPrompt {
  category: string;
  text: string;
}

interface SuggestedPromptsProps {
  onSelect: (text: string) => void;
}

const CATEGORY_COLORS: Record<string, string> = {
  "Liquidity — LCR": "bg-blue-50 border-blue-200 text-blue-800 hover:bg-blue-100",
  "Liquidity — NSFR": "bg-sky-50 border-sky-200 text-sky-800 hover:bg-sky-100",
  Capital: "bg-emerald-50 border-emerald-200 text-emerald-800 hover:bg-emerald-100",
  "Balance Sheet": "bg-teal-50 border-teal-200 text-teal-800 hover:bg-teal-100",
  ALM: "bg-amber-50 border-amber-200 text-amber-800 hover:bg-amber-100",
  "Stress Testing": "bg-orange-50 border-orange-200 text-orange-800 hover:bg-orange-100",
  Regulatory: "bg-purple-50 border-purple-200 text-purple-800 hover:bg-purple-100",
  Executive: "bg-rose-50 border-rose-200 text-rose-800 hover:bg-rose-100",
};

async function fetchSuggestedPrompts(): Promise<SuggestedPrompt[]> {
  const r = await fetch("/api/v1/copilot/suggested-prompts");
  if (!r.ok) throw new Error("Failed to load suggested prompts");
  return r.json() as Promise<SuggestedPrompt[]>;
}

export function SuggestedPrompts({ onSelect }: SuggestedPromptsProps) {
  const { data: prompts } = useQuery({
    queryKey: ["copilot-suggested-prompts"],
    queryFn: fetchSuggestedPrompts,
    staleTime: Infinity,
  });

  if (!prompts?.length) return null;

  const byCategory = prompts.reduce<Record<string, SuggestedPrompt[]>>(
    (acc, p) => {
      if (!acc[p.category]) acc[p.category] = [];
      acc[p.category].push(p);
      return acc;
    },
    {}
  );

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <p className="text-caption text-text-secondary text-center mb-4">
        Ask me anything about your regulatory position, or choose a prompt:
      </p>
      <div className="space-y-3">
        {Object.entries(byCategory).map(([cat, items]) => (
          <div key={cat}>
            <p className="text-caption font-semibold text-text-secondary uppercase tracking-wide mb-1.5">
              {cat}
            </p>
            <div className="flex flex-col gap-1.5">
              {items.map((p) => (
                <button
                  key={p.text}
                  onClick={() => onSelect(p.text)}
                  className={clsx(
                    "text-left text-sm px-3 py-2 rounded-md border transition-colors",
                    CATEGORY_COLORS[cat] ??
                      "bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100"
                  )}
                >
                  {p.text}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
