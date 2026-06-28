import { NavLink } from "react-router-dom";
import { clsx } from "clsx";
import {
  LayoutDashboard,
  Layers,
  Activity,
  LineChart,
  Building2,
  FlaskConical,
  LogOut,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/positions", label: "Positions", icon: Layers },
  { to: "/scenarios", label: "Scenarios", icon: FlaskConical },
  { to: "/analytics/lcr", label: "LCR", icon: Activity },
  { to: "/analytics/nsfr", label: "NSFR", icon: LineChart },
  { to: "/analytics/balance-sheet", label: "Balance Sheet", icon: Building2 },
];

export function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <aside className="flex h-full w-56 flex-col border-r border-border bg-surface flex-shrink-0">
      <div className="flex h-14 items-center px-4 border-b border-border">
        <span className="font-mono text-heading text-accent font-semibold">BSM</span>
        <span className="font-mono text-heading text-text-secondary ml-1">Platform</span>
      </div>

      <nav className="flex-1 overflow-y-auto px-2 py-4 space-y-0.5">
        {NAV.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 rounded-md px-3 py-2 text-body transition-colors",
                isActive
                  ? "bg-accent/10 text-accent font-medium"
                  : "text-text-secondary hover:bg-border hover:text-text-primary"
              )
            }
          >
            <Icon className="h-4 w-4 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-border p-3">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-accent/20 flex items-center justify-center text-accent text-caption font-semibold flex-shrink-0">
            {user?.name.charAt(0) ?? "?"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-caption font-medium text-text-primary truncate">
              {user?.name}
            </p>
            <p className="text-caption text-text-secondary truncate">{user?.role}</p>
          </div>
          <button
            onClick={logout}
            className="text-text-secondary hover:text-critical p-1 rounded transition-colors"
            title="Log out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
