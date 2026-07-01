import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import { TourProvider } from "./context/TourContext";
import { AppShell } from "./components/layout/AppShell";
import { LoadingSpinner } from "./components/ui/LoadingSpinner";

// Pages loaded eagerly (critical path)
import { Login } from "./pages/Login";
import { LandingPage } from "./pages/LandingPage";

// All other pages lazy-loaded for code splitting
const ExecutiveDashboard = lazy(() =>
  import("./pages/dashboard/ExecutiveDashboard").then((m) => ({ default: m.ExecutiveDashboard }))
);
const Dashboard = lazy(() =>
  import("./pages/Dashboard").then((m) => ({ default: m.Dashboard }))
);
const PositionList = lazy(() =>
  import("./pages/positions/PositionList").then((m) => ({ default: m.PositionList }))
);
const ScenarioList = lazy(() =>
  import("./pages/scenarios/ScenarioList").then((m) => ({ default: m.ScenarioList }))
);
const LCRDashboard = lazy(() =>
  import("./pages/analytics/LCRDashboard").then((m) => ({ default: m.LCRDashboard }))
);
const NSFRDashboard = lazy(() =>
  import("./pages/analytics/NSFRDashboard").then((m) => ({ default: m.NSFRDashboard }))
);
const BalanceSheetDashboard = lazy(() =>
  import("./pages/analytics/BalanceSheetDashboard").then((m) => ({ default: m.BalanceSheetDashboard }))
);
const CopilotPage = lazy(() =>
  import("./pages/copilot/CopilotPage").then((m) => ({ default: m.CopilotPage }))
);
const BriefingsPage = lazy(() =>
  import("./pages/autonomous/BriefingsPage").then((m) => ({ default: m.BriefingsPage }))
);
const IssuesPage = lazy(() =>
  import("./pages/autonomous/IssuesPage").then((m) => ({ default: m.IssuesPage }))
);
const ScheduledReportsPage = lazy(() =>
  import("./pages/autonomous/ScheduledReportsPage").then((m) => ({ default: m.ScheduledReportsPage }))
);
const AboutSAMPage = lazy(() =>
  import("./pages/AboutSAMPage").then((m) => ({ default: m.AboutSAMPage }))
);
const HelpCenterPage = lazy(() =>
  import("./pages/HelpCenterPage").then((m) => ({ default: m.HelpCenterPage }))
);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

function PageFallback() {
  return (
    <div className="flex flex-1 items-center justify-center">
      <LoadingSpinner size="md" />
    </div>
  );
}

function RequireAuth() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/welcome" replace />;
  return <AppShell />;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ThemeProvider>
          <TourProvider>
            <BrowserRouter>
              <Routes>
                <Route path="/welcome" element={<LandingPage />} />
                <Route path="/login" element={<Login />} />
                <Route element={<RequireAuth />}>
                  <Route
                    index
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <ExecutiveDashboard />
                      </Suspense>
                    }
                  />
                  <Route
                    path="dashboard/legacy"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <Dashboard />
                      </Suspense>
                    }
                  />
                  <Route
                    path="positions"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <PositionList />
                      </Suspense>
                    }
                  />
                  <Route
                    path="scenarios"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <ScenarioList />
                      </Suspense>
                    }
                  />
                  <Route
                    path="analytics/lcr"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <LCRDashboard />
                      </Suspense>
                    }
                  />
                  <Route
                    path="analytics/nsfr"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <NSFRDashboard />
                      </Suspense>
                    }
                  />
                  <Route
                    path="analytics/balance-sheet"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <BalanceSheetDashboard />
                      </Suspense>
                    }
                  />
                  <Route
                    path="copilot"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <CopilotPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="autonomous/briefings"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <BriefingsPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="autonomous/issues"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <IssuesPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="autonomous/scheduled-reports"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <ScheduledReportsPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="about-sam"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <AboutSAMPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="help"
                    element={
                      <Suspense fallback={<PageFallback />}>
                        <HelpCenterPage />
                      </Suspense>
                    }
                  />
                </Route>
              </Routes>
            </BrowserRouter>
          </TourProvider>
        </ThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
