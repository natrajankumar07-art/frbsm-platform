import { AlertCircle } from "lucide-react";

export function ErrorState({
  message = "Something went wrong. Please try again.",
}: {
  message?: string;
}) {
  return (
    <div className="flex flex-col items-center gap-3 py-12 text-text-secondary">
      <AlertCircle className="h-10 w-10 text-critical" />
      <p className="text-body">{message}</p>
    </div>
  );
}
