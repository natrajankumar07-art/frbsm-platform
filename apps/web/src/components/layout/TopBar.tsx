import { useState, useRef, useEffect } from "react";
import { ChevronDown, Moon, Sun } from "lucide-react";
import { useEntity } from "../../context/EntityContext";
import { useTheme } from "../../context/ThemeContext";

export function TopBar() {
  const { entities, selected, setSelected } = useEntity();
  const { theme, toggleTheme } = useTheme();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-surface-raised px-6 flex-shrink-0">
      <div ref={ref} className="relative">
        <button
          onClick={() => setOpen((o) => !o)}
          className="flex items-center gap-2 rounded-md border border-border px-3 py-1.5 text-body text-text-primary hover:border-accent transition-colors"
        >
          <span className="font-medium">
            {selected?.name ?? "Select entity…"}
          </span>
          <ChevronDown className="h-4 w-4 text-text-secondary" />
        </button>

        {open && entities.length > 0 && (
          <div className="absolute top-full left-0 mt-1 w-80 rounded-lg border border-border bg-surface-raised shadow-lg z-50">
            {entities.map((e) => (
              <button
                key={e.id}
                onClick={() => {
                  setSelected(e);
                  setOpen(false);
                }}
                className="flex w-full items-start gap-2 px-4 py-3 hover:bg-surface text-left border-b border-border last:border-0 transition-colors"
              >
                <div>
                  <p className="text-body font-medium text-text-primary">{e.name}</p>
                  <p className="text-caption text-text-secondary">
                    {e.code} · {e.jurisdiction} · {e.entity_type}
                  </p>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={toggleTheme}
          title={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
          className="p-1.5 rounded-md text-text-secondary hover:text-text-primary hover:bg-border dark:hover:bg-gray-700 transition-colors"
        >
          {theme === "light" ? (
            <Moon className="h-4 w-4" />
          ) : (
            <Sun className="h-4 w-4 text-amber-400" />
          )}
        </button>
        <p className="text-caption text-text-secondary font-mono">BSM Platform v2026.1</p>
      </div>
    </header>
  );
}
