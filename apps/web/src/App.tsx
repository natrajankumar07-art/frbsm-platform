import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

/**
 * Root application shell.
 *
 * Epic 1 will mount the router and global layout here.
 * For Epic 0, this renders a health-check placeholder so the build validates.
 */
export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex h-full items-center justify-center">
        <p className="text-text-secondary font-mono text-sm">
          BSM Platform — Epic 0 scaffold complete
        </p>
      </div>
    </QueryClientProvider>
  );
}
