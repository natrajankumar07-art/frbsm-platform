import { createContext, useContext, useState, useEffect, type ReactNode } from "react";

const TOUR_KEY = "bsm-tour-complete";

interface TourStep {
  id: string;
  title: string;
  description: string;
  icon: string;
}

const TOUR_STEPS: TourStep[] = [
  {
    id: "welcome",
    title: "Welcome to BSM Platform",
    description: "This guided tour will show you the key features of the AI-Powered Balance Sheet Management platform. You can dismiss this tour at any time.",
    icon: "🏦",
  },
  {
    id: "executive-dashboard",
    title: "Executive Intelligence Dashboard",
    description: "The home screen provides a real-time view of all regulatory metrics — LCR, NSFR, CET1, Leverage — with SAM's intelligent commentary. Select an entity from the top bar to see live data.",
    icon: "📊",
  },
  {
    id: "sam",
    title: "SAM — Your AI Banking Advisor",
    description: "SAM (Supervisory AI Manager) monitors your bank continuously. He never computes ratios — he reads validated engine outputs and provides expert insight. Use 'Ask SAM' on any metric for instant analysis.",
    icon: "🤖",
  },
  {
    id: "analytics",
    title: "Regulatory Analytics",
    description: "Deep-dive into LCR, NSFR, and Balance Sheet analytics with waterfall charts, component breakdowns, and historical trends. Navigate via the sidebar under Analytics.",
    icon: "📈",
  },
  {
    id: "copilot",
    title: "AI Copilot",
    description: "Ask SAM any banking question in natural language. He can generate reports, explain regulatory requirements, analyse trends, and provide remediation guidance — all grounded in your actual data.",
    icon: "💬",
  },
  {
    id: "autonomous",
    title: "Autonomous Intelligence",
    description: "SAM runs continuous monitoring every 15 minutes, generates executive briefings at 06:00 UTC, tracks outstanding issues, and surfaces prioritised recommendations — fully automated.",
    icon: "⚡",
  },
];

interface TourContextValue {
  isActive: boolean;
  currentStep: number;
  totalSteps: number;
  step: TourStep;
  next: () => void;
  prev: () => void;
  dismiss: () => void;
  restart: () => void;
}

const TourContext = createContext<TourContextValue | null>(null);

export function TourProvider({ children }: { children: ReactNode }) {
  const [isActive, setIsActive] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const completed = localStorage.getItem(TOUR_KEY);
    if (!completed) {
      setIsActive(true);
    }
  }, []);

  const next = () => {
    if (currentStep < TOUR_STEPS.length - 1) {
      setCurrentStep((s) => s + 1);
    } else {
      dismiss();
    }
  };

  const prev = () => {
    if (currentStep > 0) setCurrentStep((s) => s - 1);
  };

  const dismiss = () => {
    setIsActive(false);
    localStorage.setItem(TOUR_KEY, "1");
  };

  const restart = () => {
    localStorage.removeItem(TOUR_KEY);
    setCurrentStep(0);
    setIsActive(true);
  };

  return (
    <TourContext.Provider value={{
      isActive,
      currentStep,
      totalSteps: TOUR_STEPS.length,
      step: TOUR_STEPS[currentStep],
      next,
      prev,
      dismiss,
      restart,
    }}>
      {children}
    </TourContext.Provider>
  );
}

export function useTour() {
  const ctx = useContext(TourContext);
  if (!ctx) throw new Error("useTour must be used inside TourProvider");
  return ctx;
}
