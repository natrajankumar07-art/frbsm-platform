export interface PageMeta {
  page: number;
  size: number;
  total: number;
  pages: number;
}

export interface PagedResponse<T> {
  items: T[];
  meta: PageMeta;
}

export interface LegalEntity {
  id: string;
  code: string;
  name: string;
  lei: string | null;
  entity_type: string;
  jurisdiction: string;
  regulator: string;
  license_type: string | null;
  is_consolidated: boolean;
  is_reporting_entity: boolean;
  functional_currency: string;
  created_at: string;
  updated_at: string;
}

export interface Position {
  id: string;
  reporting_date: string;
  counterparty_id: string;
  product_code: string;
  currency: string;
  notional: string;
  booked_amount: string;
  fair_value: string;
  accrued_interest: string;
  maturity_date: string | null;
  asset_class: string;
  credit_grade: string;
  ifrs9_stage: string;
  days_past_due: number;
  hqla_level: string;
  deposit_type: string | null;
  customer_segment: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Snapshot {
  id: string;
  reporting_date: string;
  frozen_at: string;
  frozen_by: string;
  position_hash: string;
  position_count: number;
  status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Scenario {
  id: string;
  code: string;
  name: string;
  description: string | null;
  scenario_type: string;
  severity: string | null;
  is_regulatory: boolean;
  is_active: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface LCRResult {
  snapshot_id: string;
  entity_id: string;
  hqla_total: string;
  net_cash_outflows: string;
  total_outflows: string;
  total_inflows: string;
  inflow_cap_applied: boolean;
  lcr_ratio: string;
  minimum_ratio: string;
  passes: boolean;
  currency: string;
}

export interface NSFRResult {
  snapshot_id: string;
  entity_id: string;
  available_stable_funding: string;
  required_stable_funding: string;
  nsfr_ratio: string;
  minimum_ratio: string;
  passes: boolean;
  currency: string;
}

export interface CapitalResult {
  snapshot_id: string;
  entity_id: string;
  cet1_capital: string;
  additional_tier1: string;
  tier2_capital: string;
  total_capital: string;
  rwa_credit: string;
  rwa_market: string;
  rwa_operational: string;
  total_rwa: string;
  cet1_ratio: string;
  tier1_ratio: string;
  total_capital_ratio: string;
  leverage_ratio: string;
  passes_all: boolean;
  currency: string;
}

export interface BalanceSheetResult {
  snapshot_id: string;
  entity_id: string;
  total_assets: string;
  total_liabilities: string;
  total_equity: string;
  off_balance_sheet: string;
  currency: string;
  balances: boolean;
}

export interface PositionSummary {
  total_positions: number;
  total_booked_amount: string;
  by_asset_class: Record<string, string>;
  by_hqla_level: Record<string, string>;
  by_deposit_type: Record<string, string>;
  currency: string;
}

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  mode: string;
  commit: string;
}
