import { useCallback, useRef, useState } from "react";

interface SendOptions {
  entityId?: string;
  snapshotId?: string;
  sessionId?: string | null;
}

interface UseStreamingChatReturn {
  sendMessage: (message: string, options?: SendOptions) => Promise<void>;
  isStreaming: boolean;
  streamingContent: string;
  error: string | null;
  sessionId: string | null;
  clearError: () => void;
}

export function useStreamingChat(): UseStreamingChatReturn {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (message: string, options: SendOptions = {}) => {
      if (isStreaming) return;

      abortRef.current = new AbortController();
      setIsStreaming(true);
      setStreamingContent("");
      setError(null);

      try {
        const body: Record<string, unknown> = { message };
        if (options.sessionId) body.session_id = options.sessionId;
        if (options.entityId) body.entity_id = options.entityId;
        if (options.snapshotId) body.snapshot_id = options.snapshotId;

        const response = await fetch("/api/v1/copilot/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
          signal: abortRef.current.signal,
        });

        if (!response.ok || !response.body) {
          throw new Error(`API error: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // SSE events are separated by double newlines
          const events = buffer.split("\n\n");
          buffer = events.pop() ?? "";

          for (const event of events) {
            const line = event.trim();
            if (!line.startsWith("data:")) continue;

            const raw = line.slice("data:".length).trim();
            if (raw === "[DONE]") break;

            try {
              const parsed = JSON.parse(raw) as {
                type: string;
                content?: string;
                session_id?: string;
                message_id?: string;
              };

              if (parsed.type === "token" && parsed.content) {
                setStreamingContent((prev) => prev + parsed.content);
              } else if (parsed.type === "done") {
                if (parsed.session_id) setSessionId(parsed.session_id);
              } else if (parsed.type === "error") {
                setError(parsed.content ?? "Unknown error from AI provider");
              }
            } catch {
              // skip malformed JSON
            }
          }
        }
      } catch (err) {
        if (err instanceof Error && err.name !== "AbortError") {
          setError(err.message);
        }
      } finally {
        setIsStreaming(false);
      }
    },
    [isStreaming]
  );

  return {
    sendMessage,
    isStreaming,
    streamingContent,
    error,
    sessionId,
    clearError: () => setError(null),
  };
}
