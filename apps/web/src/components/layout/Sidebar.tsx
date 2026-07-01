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
  Bot,
  BarChart3,
  FileText,
  AlertTriangle,
  Clock,
  Info,
  HelpCircle,
  BookOpen,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { useTour } from "../../context/TourContext";

const NAV_PRIMARY = [
  { to: "/", label: "Executive Dashboard", icon: BarChart3, end: true },
  { to: "/positions", label: "Positions", icon: Layers },
  { to: "/scenarios", label: "Scenarios", icon: FlaskConical },
  { to: "/analytics/lcr", label: "LCR", icon: Activity },
  { to: "/analytics/nsfr", label: "NSFR", icon: LineChart },
  { to: "/analytics/balance-sheet", label: "Balance Sheet", icon: Building2 },
  { to: "/dashboard/legacy", label: "Ops Dashboard", icon: LayoutDashboard },
];

const NAV_AUTONOMOUS = [
  { to: "/autonomous/briefings", label: "Briefings", icon: FileText },
  { to: "/autonomous/issues", label: "Issues", icon: AlertTriangle },
  { to: "/autonomous/scheduled-reports", label: "Scheduled Reports", icon: Clock },
];

function NavItem({
  to,
  label,
  icon: Icon,
  end,
}: {
  to: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  end?: boolean;
}) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        clsx(
          "flex items-center gap-3 rounded-md px-3 py-2 text-body transition-colors",
          isActive
            ? "bg-accent/10 text-accent font-medium"
            : "text-text-secondary hover:bg-border hover:text-text-primary dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-100"
        )
      }
      aria-label={label}
    >
      <Icon className="h-4 w-4 flex-shrink-0" />
      {label}
    </NavLink>
  );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="px-3 pt-1 pb-0.5 text-xs font-semibold text-text-secondary/50 dark:text-gray-600 uppercase tracking-wider">
      {children}
    </p>
  );
}

export function Sidebar() {
  const { user, logout, isDemoMode } = useAuth();
  const { restart: restartTour } = useTour();

  return (
    <aside
      className="flex h-full w-56 flex-col border-r border-border dark:border-gray-800 bg-surface dark:bg-gray-950 flex-shrink-0"
      role="navigation"
      aria-label="Main navigation"
    >
      {/* Logo */}
      <div className="flex h-14 items-center justify-between px-4 border-b border-border dark:border-gray-800">
        <div className="flex items-center gap-1.5">
          <span className="font-mono text-heading text-accent font-semibold">BSM</span>
          <span className="font-mono text-heading text-text-secondary dark:text-gray-500">Platform</span>
        </div>
        {isDemoMode && (
          <span className="text-xs font-semibold text-amber-500 bg-amber-500/10 rounded px-1.5 py-0.5">
            DEMO
          </span>
        )}
      </div>

      <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-0.5">
        {/* Primary nav */}
        {NAV_PRIMARY.map(({ to, label, icon, end }) => (
          <NavItem key={to} to={to} label={label} icon={icon} end={end} />
        ))}

        {/* AI Copilot */}
        <div className="border-t border-border dark:border-gray-800 my-2" />
        <NavItem to="/copilot" label="AI Copilot" icon={Bot} />

        {/* SAM Autonomous */}
        <div className="border-t border-border dark:border-gray-800 my-2" />
        <SectionLabel>SAM Autonomous</SectionLabel>
        {NAV_AUTONOMOUS.map(({ to, label, icon }) => (
          <NavItem key={to} to={to} label={label} icon={icon} />
        ))}

        {/* SAM & Help */}
        <div className="border-t border-border dark:border-gray-800 my-2" />
        <SectionLabel>Platform</SectionLabel>
        <NavItem to="/about-sam" label="About SAM" icon={Info} />
        <NavItem to="/help" label="Help Center" icon={HelpCircle} />
        <button
          onClick={restartTour}
          className="flex items-center gap-3 rounded-md px-3 py-2 text-body text-text-secondary dark:text-gray-400 hover:bg-border hover:text-text-primary dark:hover:bg-gray-800 dark:hover:text-gray-100 transition-colors w-full text-left"
          aria-label="Restart product tour"
        >
          <BookOpen className="h-4 w-4 flex-shrink-0" />
          Product Tour
        </button>
      </nav>

      {/* User section */}
      <div className="border-t border-border dark:border-gray-800 p-3">
        <div className="flex items-center gap-2">
          <div
            className="h-8 w-8 rounded-full bg-accent/20 flex items-center justify-center text-accent text-caption font-semibold flex-shrink-0"
            aria-hidden="true"
          >
            {user?.name.charAt(0) ?? "?"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-caption font-medium text-text-primary dark:text-gray-100 truncate">
              {user?.name}
            </p>
            <p className="text-caption text-text-secondary dark:text-gray-500 truncate">{user?.role}</p>
          </div>
          <button
            onClick={logout}
            className="text-text-secondary hover:text-critical dark:hover:text-red-400 p-1 rounded transition-colors"
            title="Log out"
            aria-label="Log out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
