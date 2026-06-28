import { Inbox } from "lucide-react";

export function EmptyState({
  message = "No data available.",
}: {
  message?: string;
}) {
  return (
    <div className="flex flex-col items-center gap-3 py-12 text-text-secondary">
      <Inbox className="h-10 w-10" />
      <p className="text-body">{message}</p>
    </div>
  );
}
