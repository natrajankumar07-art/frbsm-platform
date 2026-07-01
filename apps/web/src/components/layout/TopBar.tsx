import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ChevronDown, Moon, Sun, HelpCircle, Info } from "lucide-react";
import { useEntity } from "../../context/EntityContext";
import { useTheme } from "../../context/ThemeContext";
import { useAuth } from "../../context/AuthContext";

export function TopBar() {
  const { entities, selected, setSelected } = useEntity();
  const { theme, toggleTheme } = useTheme();
  const { isDemoMode } = useAuth();
  const navigate = useNavigate();
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
    <header
      className="flex h-14 items-center justify-between border-b border-border dark:border-gray-800 bg-surface-raised dark:bg-gray-900 px-6 flex-shrink-0"
      role="banner"
    >
      {/* Entity selector */}
      <div ref={ref} className="relative">
        <button
          onClick={() => setOpen((o) => !o)}
          className="flex items-center gap-2 rounded-md border border-border dark:border-gray-700 px-3 py-1.5 text-body text-text-primary dark:text-gray-100 hover:border-accent dark:hover:border-accent transition-colors"
          aria-label="Select legal entity"
          aria-expanded={open}
          aria-haspopup="listbox"
        >
          <span className="font-medium truncate max-w-48">
            {selected?.name ?? "Select entity…"}
          </span>
          {isDemoMode && (
            <span className="text-xs text-amber-500 font-semibold bg-amber-500/10 rounded px-1 py-0.5 flex-shrink-0">
              DEMO
            </span>
          )}
          <ChevronDown className="h-4 w-4 text-text-secondary flex-shrink-0" />
        </button>

        {open && entities.length > 0 && (
          <div
            className="absolute top-full left-0 mt-1 w-80 rounded-lg border border-border dark:border-gray-700 bg-surface-raised dark:bg-gray-900 shadow-lg z-50"
            role="listbox"
            aria-label="Legal entities"
          >
            {entities.map((e) => (
              <button
                key={e.id}
                role="option"
                aria-selected={selected?.id === e.id}
                onClick={() => {
                  setSelected(e);
                  setOpen(false);
                }}
                className="flex w-full items-start gap-2 px-4 py-3 hover:bg-surface dark:hover:bg-gray-800 text-left border-b border-border dark:border-gray-800 last:border-0 transition-colors"
              >
                <div>
                  <p className="text-body font-medium text-text-primary dark:text-gray-100">{e.name}</p>
                  <p className="text-caption text-text-secondary dark:text-gray-400">
                    {e.code} · {e.jurisdiction} · {e.entity_type}
                  </p>
                </div>
                {e.is_reporting_entity && (
                  <span className="ml-auto text-xs text-accent bg-accent/10 rounded px-1.5 py-0.5 whitespace-nowrap">
                    Reporting
                  </span>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Right controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => navigate("/about-sam")}
          className="hidden sm:flex items-center gap-1.5 p-1.5 rounded-md text-text-secondary dark:text-gray-400 hover:text-text-primary dark:hover:text-gray-100 hover:bg-border dark:hover:bg-gray-800 transition-colors text-caption"
          title="About SAM"
          aria-label="About SAM"
        >
          <Info className="h-4 w-4" />
          <span className="hidden lg:inline">SAM</span>
        </button>

        <button
          onClick={() => navigate("/help")}
          className="hidden sm:flex items-center gap-1.5 p-1.5 rounded-md text-text-secondary dark:text-gray-400 hover:text-text-primary dark:hover:text-gray-100 hover:bg-border dark:hover:bg-gray-800 transition-colors text-caption"
          title="Help Center"
          aria-label="Help Center"
        >
          <HelpCircle className="h-4 w-4" />
          <span className="hidden lg:inline">Help</span>
        </button>

        <button
          onClick={toggleTheme}
          title={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
          aria-label={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
          className="p-1.5 rounded-md text-text-secondary dark:text-gray-400 hover:text-text-primary dark:hover:text-gray-100 hover:bg-border dark:hover:bg-gray-700 transition-colors"
        >
          {theme === "light" ? (
            <Moon className="h-4 w-4" />
          ) : (
            <Sun className="h-4 w-4 text-amber-400" />
          )}
        </button>

        <p className="text-caption text-text-secondary dark:text-gray-500 font-mono hidden sm:block">
          BSM v2026.1
        </p>
      </div>
    </header>
  );
}
