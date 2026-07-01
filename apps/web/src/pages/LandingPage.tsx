import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { SamAvatar } from "../components/copilot/SamAvatar";
import {
  Shield,
  TrendingUp,
  Brain,
  BarChart3,
  Zap,
  ChevronRight,
  CheckCircle2,
  ArrowRight,
  Globe2,
  Server,
  Layers,
} from "lucide-react";

const CAPABILITIES = [
  {
    icon: BarChart3,
    title: "Real-Time Regulatory Analytics",
    description: "LCR, NSFR, CET1, Tier 1, Total Capital, and Leverage ratios computed by validated Basel III engines — not estimates.",
    color: "text-accent",
    bg: "bg-accent/10",
  },
  {
    icon: Brain,
    title: "SAM — AI Banking Advisor",
    description: "Supervisory AI Manager provides executive briefings, risk analysis, and remediation guidance in natural language.",
    color: "text-purple-500",
    bg: "bg-purple-500/10",
  },
  {
    icon: Zap,
    title: "Autonomous Monitoring",
    description: "SAM monitors your balance sheet continuously, detects threshold breaches, and surfaces prioritised recommendations 24/7.",
    color: "text-amber-500",
    bg: "bg-amber-500/10",
  },
  {
    icon: TrendingUp,
    title: "Stress Testing",
    description: "Run regulatory and custom stress scenarios across your portfolio and see capital impact instantly.",
    color: "text-green-500",
    bg: "bg-green-500/10",
  },
  {
    icon: Shield,
    title: "Report Automation",
    description: "Generate CEO, CRO, Board Pack, ICAAP, ILAAP, and Liquidity Summary reports with a single click.",
    color: "text-red-500",
    bg: "bg-red-500/10",
  },
  {
    icon: Globe2,
    title: "Multi-Entity Coverage",
    description: "Manage multiple legal entities and reporting jurisdictions from a single dashboard.",
    color: "text-cyan-500",
    bg: "bg-cyan-500/10",
  },
];

const REGULATORY = [
  "Basel III / CRR II",
  "BCBS 238 (LCR)",
  "BCBS 295 (NSFR)",
  "CRD IV / CRR",
  "PRA Rulebook",
  "RBI Guidelines",
  "APRA APS 210",
  "HKMA Framework",
];

const TECH_STACK = [
  { name: "FastAPI", desc: "Python API layer" },
  { name: "React 18", desc: "Frontend framework" },
  { name: "PostgreSQL", desc: "Persistent storage" },
  { name: "Claude AI", desc: "LLM reasoning" },
  { name: "Anthropic SDK", desc: "Tool-use framework" },
  { name: "SQLAlchemy", desc: "Async ORM" },
  { name: "Alembic", desc: "DB migrations" },
  { name: "TanStack Query", desc: "Data fetching" },
];

export function LandingPage() {
  const { loginDemo } = useAuth();
  const navigate = useNavigate();
  const [launching, setLaunching] = useState(false);

  const handleLaunchDemo = async () => {
    setLaunching(true);
    await loginDemo();
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-[#0A0B0F] text-white overflow-x-hidden" data-testid="landing-page">

      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 border-b border-white/5 bg-[#0A0B0F]/80 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <span className="font-mono text-lg font-bold text-[#5C82E6]">BSM</span>
          <span className="font-mono text-lg font-light text-white/70">Platform</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("/login")}
            className="text-sm text-white/60 hover:text-white transition-colors px-3 py-1.5"
          >
            Sign in
          </button>
          <button
            onClick={handleLaunchDemo}
            disabled={launching}
            className="flex items-center gap-1.5 rounded-lg bg-[#2B5BD7] hover:bg-[#2B5BD7]/90 text-white text-sm font-medium px-4 py-2 transition-colors disabled:opacity-60"
          >
            {launching ? "Launching…" : "Launch Demo"}
            {!launching && <ArrowRight className="h-3.5 w-3.5" />}
          </button>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-32 pb-20 px-6 text-center overflow-hidden">
        {/* Background glow */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_50%_20%,rgba(43,91,215,0.15)_0%,transparent_70%)]" />
        <div className="absolute top-24 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-[#2B5BD7]/10 blur-[100px] rounded-full" />

        <div className="relative max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 rounded-full border border-[#2B5BD7]/40 bg-[#2B5BD7]/10 px-4 py-1.5 text-sm text-[#5C82E6] mb-8">
            <span className="h-1.5 w-1.5 rounded-full bg-[#5C82E6] animate-pulse" />
            AI-Powered Banking Intelligence Platform
          </div>

          <h1 className="text-4xl sm:text-6xl font-bold tracking-tight mb-6 leading-tight">
            Enterprise Balance Sheet{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#5C82E6] to-[#7B9FF5]">
              Management
            </span>
          </h1>

          <p className="text-lg text-white/60 max-w-2xl mx-auto mb-10 leading-relaxed">
            Real-time Basel III regulatory analytics, autonomous AI monitoring,
            and executive intelligence — powered by validated financial engines
            and SAM, your Senior Banking Intelligence Advisor.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <button
              onClick={handleLaunchDemo}
              disabled={launching}
              className="flex items-center gap-2 rounded-xl bg-[#2B5BD7] hover:bg-[#2B5BD7]/90 text-white font-semibold px-8 py-3.5 text-base transition-all disabled:opacity-60 shadow-[0_0_24px_rgba(43,91,215,0.4)] hover:shadow-[0_0_32px_rgba(43,91,215,0.6)]"
            >
              {launching ? "Launching Demo…" : "Launch Interactive Demo"}
              {!launching && <ChevronRight className="h-4 w-4" />}
            </button>
            <button
              onClick={() => navigate("/login")}
              className="flex items-center gap-2 rounded-xl border border-white/10 hover:border-white/20 text-white/70 hover:text-white font-medium px-6 py-3.5 text-base transition-colors"
            >
              Sign in
            </button>
          </div>

          <p className="text-sm text-white/30 mt-4">No account required · Pre-loaded with demo data</p>
        </div>
      </section>

      {/* SAM Introduction */}
      <section className="py-16 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-8 sm:p-12 flex flex-col sm:flex-row items-center gap-8">
            <div className="flex-shrink-0">
              <div className="relative">
                <SamAvatar size="lg" glow statusDot />
                <div className="absolute -inset-3 rounded-full bg-[#2B5BD7]/20 blur-lg" />
              </div>
            </div>
            <div className="flex-1 text-center sm:text-left">
              <div className="flex items-center gap-2 justify-center sm:justify-start mb-2">
                <span className="font-bold text-xl">SAM</span>
                <span className="text-xs text-green-400 font-medium">● Online</span>
              </div>
              <p className="text-sm text-white/50 mb-4">Supervisory AI Manager · Senior Banking Intelligence Advisor</p>
              <p className="text-white/70 leading-relaxed text-base">
                "Good morning. I monitor your bank's regulatory position continuously — LCR, NSFR,
                capital adequacy, and leverage ratios. I never compute financial ratios myself;
                I read validated engine outputs and translate them into executive intelligence.
                Think of me as your always-on CRO analyst."
              </p>
              <div className="flex items-center gap-3 mt-6 justify-center sm:justify-start">
                <button
                  onClick={() => { navigate("/about-sam"); }}
                  className="text-sm text-[#5C82E6] hover:text-[#7B9FF5] transition-colors flex items-center gap-1"
                >
                  Learn about SAM <ChevronRight className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Capabilities */}
      <section className="py-16 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold mb-3">Platform Capabilities</h2>
            <p className="text-white/50">Everything a modern bank needs for regulatory compliance and risk management</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {CAPABILITIES.map((cap) => {
              const Icon = cap.icon;
              return (
                <div
                  key={cap.title}
                  className="rounded-xl border border-white/10 bg-white/5 p-5 hover:border-white/20 hover:bg-white/8 transition-all group"
                >
                  <div className={`inline-flex items-center justify-center rounded-lg p-2.5 mb-4 ${cap.bg}`}>
                    <Icon className={`h-5 w-5 ${cap.color}`} />
                  </div>
                  <h3 className="font-semibold text-white mb-2">{cap.title}</h3>
                  <p className="text-sm text-white/50 leading-relaxed">{cap.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section className="py-16 px-6 border-t border-white/5">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold mb-3">Three-Layer Architecture</h2>
            <p className="text-white/50">Financial engines and AI reasoning are deliberately separated</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              {
                layer: "Layer 1",
                icon: Layers,
                name: "Compute Layer",
                desc: "Basel III engines written in pure Python. LCR, NSFR, CET1, leverage, and stress test calculations. No AI involved. Deterministic and auditable.",
                color: "border-green-500/30 bg-green-500/5",
                badge: "bg-green-500/20 text-green-400",
              },
              {
                layer: "Layer 2",
                icon: Server,
                name: "Tool Layer",
                desc: "15 structured tools expose engine outputs to the reasoning layer. SAM calls tools — it never computes ratios directly. Clean separation of concerns.",
                color: "border-blue-500/30 bg-blue-500/5",
                badge: "bg-blue-500/20 text-blue-400",
              },
              {
                layer: "Layer 3",
                icon: Brain,
                name: "Reasoning Layer",
                desc: "Claude AI reads engine outputs and generates executive intelligence — explanations, recommendations, briefings, and regulatory guidance.",
                color: "border-purple-500/30 bg-purple-500/5",
                badge: "bg-purple-500/20 text-purple-400",
              },
            ].map((l) => {
              const Icon = l.icon;
              return (
                <div key={l.name} className={`rounded-xl border p-5 ${l.color}`}>
                  <div className="flex items-center gap-2 mb-3">
                    <Icon className="h-4 w-4 text-white/60" />
                    <span className={`text-xs font-semibold rounded-full px-2 py-0.5 ${l.badge}`}>
                      {l.layer}
                    </span>
                  </div>
                  <h3 className="font-bold text-white mb-2">{l.name}</h3>
                  <p className="text-sm text-white/50 leading-relaxed">{l.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Regulatory Coverage */}
      <section className="py-16 px-6 border-t border-white/5">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold mb-3">Regulatory Coverage</h2>
            <p className="text-white/50">Built for global banking regulations</p>
          </div>
          <div className="flex flex-wrap justify-center gap-3">
            {REGULATORY.map((r) => (
              <div
                key={r}
                className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-4 py-2.5"
              >
                <CheckCircle2 className="h-3.5 w-3.5 text-green-400 flex-shrink-0" />
                <span className="text-sm text-white/70">{r}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="py-16 px-6 border-t border-white/5">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold mb-3">Technology Stack</h2>
            <p className="text-white/50">Production-grade components throughout</p>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {TECH_STACK.map((t) => (
              <div key={t.name} className="rounded-lg border border-white/10 bg-white/5 p-3 text-center">
                <p className="font-mono font-semibold text-[#5C82E6]">{t.name}</p>
                <p className="text-xs text-white/40 mt-0.5">{t.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 border-t border-white/5">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl sm:text-3xl font-bold mb-4">
            Ready to see it in action?
          </h2>
          <p className="text-white/50 mb-8">
            Launch the interactive demo with pre-loaded Demo Bank data.
            No account or setup required.
          </p>
          <button
            onClick={handleLaunchDemo}
            disabled={launching}
            className="inline-flex items-center gap-2 rounded-xl bg-[#2B5BD7] hover:bg-[#2B5BD7]/90 text-white font-semibold px-10 py-4 text-base transition-all disabled:opacity-60 shadow-[0_0_32px_rgba(43,91,215,0.4)] hover:shadow-[0_0_40px_rgba(43,91,215,0.6)]"
          >
            {launching ? "Launching…" : "Launch Demo"}
            {!launching && <ArrowRight className="h-4 w-4" />}
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8 px-6 text-center text-white/30 text-sm">
        <div className="flex flex-wrap justify-center items-center gap-4">
          <span className="font-mono text-[#5C82E6] font-semibold">BSM Platform</span>
          <span>v2026.1.0</span>
          <span>·</span>
          <span>AI-Powered Balance Sheet Management</span>
          <span>·</span>
          <button onClick={() => navigate("/about-sam")} className="hover:text-white/60 transition-colors">
            About SAM
          </button>
          <span>·</span>
          <button onClick={() => navigate("/help")} className="hover:text-white/60 transition-colors">
            Help
          </button>
        </div>
      </footer>
    </div>
  );
}
