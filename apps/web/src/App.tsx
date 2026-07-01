import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import { AppShell } from "./components/layout/AppShell";
import { Login } from "./pages/Login";
import { ExecutiveDashboard } from "./pages/dashboard/ExecutiveDashboard";
import { Dashboard } from "./pages/Dashboard";
import { PositionList } from "./pages/positions/PositionList";
import { ScenarioList } from "./pages/scenarios/ScenarioList";
import { LCRDashboard } from "./pages/analytics/LCRDashboard";
import { NSFRDashboard } from "./pages/analytics/NSFRDashboard";
import { BalanceSheetDashboard } from "./pages/analytics/BalanceSheetDashboard";
import { CopilotPage } from "./pages/copilot/CopilotPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

function RequireAuth() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <AppShell />;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ThemeProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route element={<RequireAuth />}>
              <Route index element={<ExecutiveDashboard />} />
              <Route path="dashboard/legacy" element={<Dashboard />} />
              <Route path="positions" element={<PositionList />} />
              <Route path="scenarios" element={<ScenarioList />} />
              <Route path="analytics/lcr" element={<LCRDashboard />} />
              <Route path="analytics/nsfr" element={<NSFRDashboard />} />
              <Route path="analytics/balance-sheet" element={<BalanceSheetDashboard />} />
              <Route path="copilot" element={<CopilotPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
        </ThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
