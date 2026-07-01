import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { clsx } from "clsx";
import { SamAvatar } from "./SamAvatar";

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: Date;
  isStreaming?: boolean;
}

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  if (message.role === "system") return null;

  const isUser = message.role === "user";

  return (
    <div
      className={clsx(
        "flex w-full mb-4",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <div className="mr-2 mt-0.5">
          <SamAvatar size="xs" glow={false} />
        </div>
      )}

      <div
        className={clsx(
          "max-w-[78%] rounded-lg px-4 py-3 text-body",
          isUser
            ? "bg-accent text-white rounded-br-none"
            : "bg-surface border border-border text-text-primary rounded-bl-none shadow-sm"
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        ) : (
          <div
            className={clsx(
              "prose prose-sm max-w-none",
              "prose-headings:text-text-primary prose-headings:font-semibold",
              "prose-p:text-text-primary prose-p:leading-relaxed",
              "prose-strong:text-text-primary prose-strong:font-semibold",
              "prose-code:text-accent prose-code:bg-accent/10 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-sm",
              "prose-pre:bg-gray-900 prose-pre:text-gray-100 prose-pre:rounded-md",
              "prose-ul:text-text-primary prose-ol:text-text-primary",
              "prose-li:text-text-primary prose-li:leading-relaxed",
              "prose-blockquote:border-l-accent prose-blockquote:text-text-secondary",
              message.isStreaming && "after:content-['▋'] after:ml-0.5 after:animate-pulse after:text-accent"
            )}
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}

        {message.timestamp && (
          <p
            className={clsx(
              "text-caption mt-1.5",
              isUser ? "text-white/60" : "text-text-secondary"
            )}
          >
            {message.timestamp.toLocaleTimeString("en-IN", {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </p>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-7 h-7 rounded-full bg-accent flex items-center justify-center text-white text-caption font-bold ml-2 mt-0.5">
          U
        </div>
      )}
    </div>
  );
}
