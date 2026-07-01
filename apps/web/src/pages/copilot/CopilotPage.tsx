import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { useQuery } from "@tanstack/react-query";
import { Bot, Plus, Send, Trash2, AlertCircle, FileText, ShieldCheck, LayoutList, Bell } from "lucide-react";
import { clsx } from "clsx";
import { useStreamingChat } from "../../hooks/useStreamingChat";
import { ChatMessage, type Message } from "../../components/copilot/ChatMessage";
import { SuggestedPrompts } from "../../components/copilot/SuggestedPrompts";
import { ReportPanel } from "../../components/copilot/ReportPanel";
import { EvidencePanel } from "../../components/copilot/EvidencePanel";
import { AgentProfile } from "../../components/copilot/AgentProfile";
import { ExecutionTimeline, type TimelineEvent } from "../../components/copilot/ExecutionTimeline";
import { PlannerPanel, type ActivePlan } from "../../components/copilot/PlannerPanel";
import { AlertPanel } from "../../components/copilot/AlertPanel";
import { useEntity } from "../../context/EntityContext";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import type { ToolEvidence } from "../../types/workflow";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Session {
  id: string;
  title: string;
  entity_id: string | null;
  created_at: string;
  updated_at: string;
}

interface ApiMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
}

// ---------------------------------------------------------------------------
// API helpers (raw fetch — TanStack Query for GETs, raw for streaming POST)
// ---------------------------------------------------------------------------

async function fetchSessions(): Promise<Session[]> {
  const r = await fetch("/api/v1/copilot/sessions?size=50");
  if (!r.ok) throw new Error("Failed to load sessions");
  const data = (await r.json()) as { items: Session[] };
  return data.items;
}

async function fetchMessages(sessionId: string): Promise<ApiMessage[]> {
  const r = await fetch(`/api/v1/copilot/sessions/${sessionId}/messages`);
  if (!r.ok) throw new Error("Failed to load messages");
  return r.json() as Promise<ApiMessage[]>;
}

async function deleteSession(sessionId: string): Promise<void> {
  await fetch(`/api/v1/copilot/sessions/${sessionId}`, { method: "DELETE" });
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function CopilotPage() {
  const { selected: entity } = useEntity();

  // Active session state
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { sendMessage, isStreaming, streamingContent, error, sessionId, clearError } =
    useStreamingChat();

  // Load sessions list
  const {
    data: sessions,
    refetch: refetchSessions,
  } = useQuery({
    queryKey: ["copilot-sessions"],
    queryFn: fetchSessions,
    staleTime: 5_000,
  });

  // When streaming produces a new session, adopt it
  useEffect(() => {
    if (sessionId && sessionId !== activeSessionId) {
      setActiveSessionId(sessionId);
      void refetchSessions();
    }
  }, [sessionId, activeSessionId, refetchSessions]);

  // Load messages when switching session
  useEffect(() => {
    if (!activeSessionId) return;
    void fetchMessages(activeSessionId).then((apiMsgs) => {
      setMessages(
        apiMsgs
          .filter((m) => m.role !== "system")
          .map((m) => ({
            id: m.id,
            role: m.role,
            content: m.content,
            timestamp: new Date(m.created_at),
          }))
      );
    });
  }, [activeSessionId]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  // ---------------------------------------------------------------------------
  // Send handler
  // ---------------------------------------------------------------------------

  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text || isStreaming) return;

    const userMsg: Message = {
      id: `tmp-${Date.now()}`,
      role: "user",
      content: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setAgentStatus("thinking");

    await sendMessage(text, {
      sessionId: activeSessionId,
      entityId: entity?.id,
    });

    // After streaming completes, reload messages from server to get proper IDs
    if (sessionId || activeSessionId) {
      const sid = sessionId ?? activeSessionId!;
      const refreshed = await fetchMessages(sid);
      setMessages(
        refreshed
          .filter((m) => m.role !== "system")
          .map((m) => ({
            id: m.id,
            role: m.role,
            content: m.content,
            timestamp: new Date(m.created_at),
          }))
      );
      void refetchSessions();
    }
    setAgentStatus("idle");
  }, [input, isStreaming, sendMessage, activeSessionId, entity?.id, sessionId, refetchSessions]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSend();
    }
  };

  const handleNewChat = () => {
    setActiveSessionId(null);
    setMessages([]);
    setInput("");
    clearError();
  };

  const handleSelectSession = (id: string) => {
    if (id === activeSessionId) return;
    setActiveSessionId(id);
    clearError();
  };

  const handleDeleteSession = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    await deleteSession(id);
    if (id === activeSessionId) handleNewChat();
    void refetchSessions();
  };

  const handleSuggestedPrompt = (text: string) => {
    setInput(text);
    textareaRef.current?.focus();
  };

  const isEmpty = messages.length === 0 && !isStreaming;

  // Right panel tab state
  const [rightTab, setRightTab] = useState<"reports" | "evidence" | "planner" | "alerts">("reports");
  const [lastEvidence, setLastEvidence] = useState<ToolEvidence | null>(null);
  const [agentTimeline, setAgentTimeline] = useState<TimelineEvent[]>([]);
  const [activePlan, setActivePlan] = useState<ActivePlan | null>(null);
  const [agentStatus, setAgentStatus] = useState<"idle" | "thinking" | "active">("idle");

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <div className="flex h-full" style={{ height: "calc(100vh - 56px)" }}>
      {/* ── Left panel: session history ──────────────────────────────────── */}
      <aside className="w-56 flex-shrink-0 border-r border-border bg-surface flex flex-col">
        <div className="p-3 border-b border-border">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-md bg-accent text-white text-body font-medium hover:bg-accent/90 transition-colors"
          >
            <Plus className="h-4 w-4" />
            New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-2">
          {!sessions?.length ? (
            <p className="text-caption text-text-secondary px-3 py-4 text-center">
              No conversations yet
            </p>
          ) : (
            sessions.map((s) => (
              <button
                key={s.id}
                onClick={() => handleSelectSession(s.id)}
                className={clsx(
                  "w-full text-left px-3 py-2 text-caption rounded-md mx-1 flex items-start gap-1 group transition-colors",
                  activeSessionId === s.id
                    ? "bg-accent/10 text-accent font-medium"
                    : "text-text-secondary hover:bg-border hover:text-text-primary"
                )}
              >
                <Bot className="h-3.5 w-3.5 mt-0.5 flex-shrink-0" />
                <span className="flex-1 truncate">{s.title}</span>
                <span
                  onClick={(e) => void handleDeleteSession(s.id, e)}
                  className="opacity-0 group-hover:opacity-100 text-text-secondary hover:text-critical transition-opacity cursor-pointer"
                  role="button"
                  aria-label="Delete session"
                >
                  <Trash2 className="h-3 w-3" />
                </span>
              </button>
            ))
          )}
        </div>
      </aside>

      {/* ── Main panel: chat ─────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0 border-r border-border">
        {/* Header */}
        <div className="h-14 border-b border-border flex items-center px-6 flex-shrink-0 gap-3">
          <AgentProfile
            name="SAM"
            title="Supervisory AI Manager"
            status={agentStatus}
            compact
          />
          {entity && (
            <span className="text-caption text-text-secondary ml-1">
              · {entity.name}
            </span>
          )}
          {isStreaming && (
            <span className="ml-auto text-caption text-accent animate-pulse">
              Generating…
            </span>
          )}
        </div>

        {/* Message area */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {isEmpty ? (
            <div className="flex flex-col items-center justify-center h-full">
              <div className="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center mb-4">
                <Bot className="h-6 w-6 text-accent" />
              </div>
              <h2 className="text-heading font-semibold text-text-primary mb-1">
                FRBSM AI Copilot
              </h2>
              <p className="text-body text-text-secondary text-center mb-6 max-w-sm">
                I explain your regulatory position using results computed by the BSM
                engines — I never recalculate them myself.
              </p>
              <SuggestedPrompts onSelect={handleSuggestedPrompt} />
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}

              {/* Streaming bubble */}
              {isStreaming && streamingContent && (
                <ChatMessage
                  message={{
                    id: "streaming",
                    role: "assistant",
                    content: streamingContent,
                    isStreaming: true,
                  }}
                />
              )}

              {/* Thinking indicator (streaming started but no content yet) */}
              {isStreaming && !streamingContent && (
                <div className="flex justify-start mb-4">
                  <div className="flex-shrink-0 w-7 h-7 rounded-full bg-accent/20 flex items-center justify-center text-accent text-caption font-bold mr-2">
                    AI
                  </div>
                  <div className="bg-surface border border-border rounded-lg rounded-bl-none px-4 py-3">
                    <LoadingSpinner />
                  </div>
                </div>
              )}
            </>
          )}

          {/* Error banner */}
          {error && (
            <div className="flex items-start gap-2 bg-red-50 border border-red-200 rounded-md px-4 py-3 mb-4">
              <AlertCircle className="h-4 w-4 text-red-500 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-red-700">{error}</p>
              </div>
              <button
                onClick={clearError}
                className="text-red-400 hover:text-red-600 text-caption"
              >
                ✕
              </button>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="border-t border-border p-4 flex-shrink-0">
          <div className="flex gap-2 items-end">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about LCR, NSFR, capital ratios, regulatory frameworks…"
              rows={2}
              disabled={isStreaming}
              className={clsx(
                "flex-1 resize-none rounded-md border border-border bg-white px-3 py-2",
                "text-body text-text-primary placeholder:text-text-secondary",
                "focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                "transition-colors"
              )}
            />
            <button
              onClick={() => void handleSend()}
              disabled={!input.trim() || isStreaming}
              className={clsx(
                "flex-shrink-0 h-10 w-10 rounded-md flex items-center justify-center transition-colors",
                input.trim() && !isStreaming
                  ? "bg-accent text-white hover:bg-accent/90"
                  : "bg-border text-text-secondary cursor-not-allowed"
              )}
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
          <p className="text-caption text-text-secondary mt-1.5">
            Enter to send · Shift+Enter for new line
          </p>
        </div>
      </div>
      {/* ── Right panel: Reports + Evidence + Planner + Alerts ──────────── */}
      <aside className="w-72 flex-shrink-0 bg-surface flex flex-col">
        {/* Tab bar — 4 tabs */}
        <div className="flex border-b border-border">
          {(
            [
              { id: "reports", icon: <FileText className="h-3 w-3" />, label: "Reports" },
              { id: "evidence", icon: <ShieldCheck className="h-3 w-3" />, label: "Evidence" },
              { id: "planner", icon: <LayoutList className="h-3 w-3" />, label: "Plan" },
              { id: "alerts", icon: <Bell className="h-3 w-3" />, label: "Alerts" },
            ] as const
          ).map(({ id, icon, label }) => (
            <button
              key={id}
              onClick={() => setRightTab(id)}
              className={clsx(
                "flex-1 flex items-center justify-center gap-1 py-2.5 text-caption font-medium transition-colors",
                rightTab === id
                  ? "text-accent border-b-2 border-accent"
                  : "text-text-secondary hover:text-text-primary"
              )}
            >
              {icon}
              {label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="flex-1 overflow-y-auto">
          {rightTab === "reports" && (
            <ReportPanel entityId={entity?.id ?? null} />
          )}
          {rightTab === "evidence" && (
            <EvidencePanel evidence={lastEvidence} toolCallsLog={[]} />
          )}
          {rightTab === "planner" && (
            <div className="space-y-3 py-2">
              <ExecutionTimeline events={agentTimeline} planId={activePlan?.plan_id} />
              {activePlan && (
                <div className="border-t border-border pt-2">
                  <PlannerPanel plan={activePlan} isExecuting={isStreaming} />
                </div>
              )}
            </div>
          )}
          {rightTab === "alerts" && <AlertPanel />}
        </div>
      </aside>
    </div>
  );
}
