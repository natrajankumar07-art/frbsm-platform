import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { EntityProvider } from "../../context/EntityContext";

export function AppShell() {
  return (
    <EntityProvider>
      <div className="flex h-screen overflow-hidden bg-surface">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <TopBar />
          <main className="flex-1 overflow-y-auto p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </EntityProvider>
  );
}
