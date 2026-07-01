import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { ProductTour } from "./ProductTour";
import { EntityProvider } from "../../context/EntityContext";

export function AppShell() {
  return (
    <EntityProvider>
      <div className="flex h-screen overflow-hidden bg-surface dark:bg-gray-950">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <TopBar />
          <main
            className="flex-1 overflow-y-auto p-6"
            id="main-content"
            role="main"
            aria-label="Main content"
          >
            <Outlet />
          </main>
        </div>
      </div>
      <ProductTour />
    </EntityProvider>
  );
}
