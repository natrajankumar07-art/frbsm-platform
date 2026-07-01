import { useNavigate } from "react-router-dom";
import { clsx } from "clsx";

interface AskSAMButtonProps {
  context: string;
  label?: string;
  size?: "xs" | "sm";
  className?: string;
}

export function AskSAMButton({
  context,
  label = "Ask SAM",
  size = "sm",
  className,
}: AskSAMButtonProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    sessionStorage.setItem("bsm-copilot-prefill", context);
    navigate("/copilot");
  };

  return (
    <button
      onClick={handleClick}
      data-testid="ask-sam-button"
      className={clsx(
        "rounded-md font-medium transition-colors",
        "bg-accent/10 text-accent hover:bg-accent/20",
        "dark:bg-blue-900/40 dark:text-blue-400 dark:hover:bg-blue-800/50",
        size === "xs" ? "text-xs px-2 py-0.5" : "text-xs px-2.5 py-1",
        className
      )}
    >
      {label} →
    </button>
  );
}
