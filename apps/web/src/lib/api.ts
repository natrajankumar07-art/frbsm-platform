import axios from "axios";
import type {
  LegalEntity,
  Position,
  Snapshot,
  Scenario,
  LCRResult,
  NSFRResult,
  CapitalResult,
  BalanceSheetResult,
  PositionSummary,
  PagedResponse,
  HealthStatus,
} from "../types/api";

export const http = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
  timeout: 15_000,
});

const get = <T>(url: string, params?: Record<string, unknown>) =>
  http.get<T>(url, { params }).then((r) => r.data);

export const api = {
  health: {
    live: () => get<HealthStatus>("/health"),
    ready: () => get<HealthStatus>("/health"),
  },
  legalEntities: {
    list: (params?: { page?: number; size?: number }) =>
      get<PagedResponse<LegalEntity>>("/v1/legal-entities", params as Record<string, unknown>),
    get: (id: string) => get<LegalEntity>(`/v1/legal-entities/${id}`),
  },
  positions: {
    list: (params?: { page?: number; size?: number; sort_by?: string }) =>
      get<PagedResponse<Position>>("/v1/positions", params as Record<string, unknown>),
    get: (id: string) => get<Position>(`/v1/positions/${id}`),
  },
  snapshots: {
    list: (params?: { page?: number; size?: number; sort_by?: string }) =>
      get<PagedResponse<Snapshot>>("/v1/snapshots", params as Record<string, unknown>),
    get: (id: string) => get<Snapshot>(`/v1/snapshots/${id}`),
  },
  scenarios: {
    list: (params?: { page?: number; size?: number }) =>
      get<PagedResponse<Scenario>>("/v1/scenarios", params as Record<string, unknown>),
    get: (id: string) => get<Scenario>(`/v1/scenarios/${id}`),
  },
  analytics: {
    lcr: (snapshotId: string, entityId: string) =>
      get<LCRResult | null>("/v1/analytics/lcr", {
        snapshot_id: snapshotId,
        entity_id: entityId,
      }),
    nsfr: (snapshotId: string, entityId: string) =>
      get<NSFRResult | null>("/v1/analytics/nsfr", {
        snapshot_id: snapshotId,
        entity_id: entityId,
      }),
    capital: (snapshotId: string, entityId: string) =>
      get<CapitalResult | null>("/v1/analytics/capital", {
        snapshot_id: snapshotId,
        entity_id: entityId,
      }),
    balanceSheet: (snapshotId: string, entityId: string) =>
      get<BalanceSheetResult | null>("/v1/analytics/balance-sheet", {
        snapshot_id: snapshotId,
        entity_id: entityId,
      }),
    positionSummary: (entityId: string, snapshotId?: string) =>
      get<PositionSummary>("/v1/analytics/positions/summary", {
        entity_id: entityId,
        ...(snapshotId ? { snapshot_id: snapshotId } : {}),
      }),
  },
};
