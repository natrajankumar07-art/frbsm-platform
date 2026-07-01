import { createContext, useContext, useState, type ReactNode } from "react";

interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isDemoMode: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginDemo: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const DEMO_USER: AuthUser = {
  id: "demo-user-001",
  name: "Demo User",
  email: "demo@bsmplatform.in",
  role: "Risk Analyst",
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isDemoMode, setIsDemoMode] = useState(false);

  const login = async (_email: string, _password: string) => {
    await new Promise((r) => setTimeout(r, 400));
    setUser(DEMO_USER);
    setIsDemoMode(false);
  };

  const loginDemo = async () => {
    await new Promise((r) => setTimeout(r, 200));
    setUser(DEMO_USER);
    setIsDemoMode(true);
  };

  const logout = () => {
    setUser(null);
    setIsDemoMode(false);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isDemoMode, login, loginDemo, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
