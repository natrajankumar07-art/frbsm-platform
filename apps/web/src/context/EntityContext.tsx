import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import type { LegalEntity } from "../types/api";

interface EntityContextValue {
  entities: LegalEntity[];
  selected: LegalEntity | null;
  setSelected: (e: LegalEntity) => void;
  isLoading: boolean;
}

const EntityContext = createContext<EntityContextValue | null>(null);

export function EntityProvider({ children }: { children: ReactNode }) {
  const [selected, setSelected] = useState<LegalEntity | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["legal-entities"],
    queryFn: () => api.legalEntities.list({ size: 50 }),
  });

  const entities = data?.items ?? [];

  useEffect(() => {
    if (entities.length > 0 && !selected) {
      const reporting = entities.find((e) => e.is_reporting_entity);
      setSelected(reporting ?? entities[0]);
    }
  }, [entities, selected]);

  return (
    <EntityContext.Provider value={{ entities, selected, setSelected, isLoading }}>
      {children}
    </EntityContext.Provider>
  );
}

export function useEntity() {
  const ctx = useContext(EntityContext);
  if (!ctx) throw new Error("useEntity must be used inside EntityProvider");
  return ctx;
}
