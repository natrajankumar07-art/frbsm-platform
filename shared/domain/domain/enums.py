"""
All categorical enumerations used across the platform.

These are the canonical enum definitions. Engine, reasoning, API, and report
layers all import from here. Never redefine these elsewhere.
"""

from enum import StrEnum


class IFRS9Stage(StrEnum):
    """IFRS 9 impairment stage classification."""

    STAGE_1 = "stage_1"  # Performing; 12-month ECL
    STAGE_2 = "stage_2"  # SICR observed; lifetime ECL
    STAGE_3 = "stage_3"  # Credit-impaired; lifetime ECL, PD=100%


class AssetClass(StrEnum):
    """Basel III Standardised Approach asset classes (Table 2, CRE20)."""

    SOVEREIGN = "sovereign"
    CENTRAL_BANK = "central_bank"
    PSE = "pse"  # Public sector entity
    MDB = "mdb"  # Multilateral development bank
    BANK = "bank"
    COVERED_BOND = "covered_bond"
    SECURITIES_FIRM = "securities_firm"
    CORPORATE = "corporate"
    SME_CORPORATE = "sme_corporate"
    RETAIL = "retail"
    SME_RETAIL = "sme_retail"
    RESIDENTIAL_MORTGAGE = "residential_mortgage"
    COMMERCIAL_REAL_ESTATE = "commercial_real_estate"
    LAND_ADC = "land_adc"  # Acquisition, development, construction
    EQUITY = "equity"
    SUBORDINATED_DEBT = "subordinated_debt"
    SECURITISATION = "securitisation"
    OTHER = "other"


class CurrencyCode(StrEnum):
    """ISO 4217 currency codes supported in v1."""

    INR = "INR"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    SGD = "SGD"
    AED = "AED"
    CHF = "CHF"
    AUD = "AUD"
    CAD = "CAD"
    HKD = "HKD"


class Jurisdiction(StrEnum):
    """Regulatory jurisdictions supported in v1. COREP/EU deferred to v2."""

    IN = "IN"  # India — RBI
    US = "US"  # United States — Federal Reserve / OCC
    # EU = "EU"  # v2 — COREP/FINREP


class PositionStatus(StrEnum):
    """Lifecycle status of a balance-sheet position."""

    ACTIVE = "active"
    MATURED = "matured"
    DEFAULTED = "defaulted"
    WRITTEN_OFF = "written_off"
    SOLD = "sold"


class CollateralType(StrEnum):
    """Types of credit risk mitigant recognised under Basel III CRM."""

    CASH = "cash"
    SOVEREIGN_BOND = "sovereign_bond"
    CORPORATE_BOND = "corporate_bond"
    EQUITY_LISTED = "equity_listed"
    EQUITY_UNLISTED = "equity_unlisted"
    PROPERTY_RESIDENTIAL = "property_residential"
    PROPERTY_COMMERCIAL = "property_commercial"
    GUARANTEE = "guarantee"
    CREDIT_DERIVATIVE = "credit_derivative"
    GOLD = "gold"
    OTHER = "other"


class RatingGrade(StrEnum):
    """External credit ratings mapped to Basel SA buckets."""

    AAA = "AAA"
    AA_PLUS = "AA+"
    AA = "AA"
    AA_MINUS = "AA-"
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    BBB_PLUS = "BBB+"
    BBB = "BBB"
    BBB_MINUS = "BBB-"
    BB_PLUS = "BB+"
    BB = "BB"
    BB_MINUS = "BB-"
    B_PLUS = "B+"
    B = "B"
    B_MINUS = "B-"
    CCC_PLUS = "CCC+"
    CCC = "CCC"
    CCC_MINUS = "CCC-"
    D = "D"
    UNRATED = "UNRATED"


class HQLALevel(StrEnum):
    """High-Quality Liquid Asset classification per Basel III LCR (LCR30)."""

    LEVEL_1 = "level_1"    # 0% haircut
    LEVEL_2A = "level_2a"  # 15% haircut; ≤40% of HQLA
    LEVEL_2B = "level_2b"  # 25–50% haircut; ≤15% of HQLA
    INELIGIBLE = "ineligible"


class DepositType(StrEnum):
    """Deposit run-off categories per Basel III LCR (LCR40)."""

    RETAIL_STABLE = "retail_stable"
    RETAIL_LESS_STABLE = "retail_less_stable"
    SMALL_BUSINESS_STABLE = "small_business_stable"
    SMALL_BUSINESS_LESS_STABLE = "small_business_less_stable"
    OPERATIONAL_DEPOSIT = "operational_deposit"
    NON_OPERATIONAL_DEPOSIT_FINANCIAL = "non_operational_deposit_financial"
    NON_OPERATIONAL_DEPOSIT_NON_FINANCIAL = "non_operational_deposit_non_financial"
    UNSECURED_WHOLESALE_FINANCIAL = "unsecured_wholesale_financial"
    UNSECURED_WHOLESALE_NON_FINANCIAL = "unsecured_wholesale_non_financial"
    SECURED_FUNDING = "secured_funding"


class CustomerSegment(StrEnum):
    """Customer segment for run-off and product behavioural assumptions."""

    RETAIL = "retail"
    SMALL_BUSINESS = "small_business"
    CORPORATE = "corporate"
    FINANCIAL_INSTITUTION = "financial_institution"
    SOVEREIGN = "sovereign"
    CENTRAL_BANK = "central_bank"


class SnapshotStatus(StrEnum):
    """Lifecycle of a point-in-time data snapshot."""

    DRAFT = "draft"    # Being assembled; mutable
    LOCKED = "locked"  # Frozen for computation; immutable
    FILED = "filed"    # Used in a regulatory filing


class UserRole(StrEnum):
    """RBAC roles. Segregation of duties: preparer ≠ reviewer ≠ approver."""

    VIEWER = "viewer"
    PREPARER = "preparer"
    REVIEWER = "reviewer"
    APPROVER = "approver"
    ADMIN = "admin"
    DEMO_ADMIN = "demo_admin"


class AppMode(StrEnum):
    """Tenant operating mode — controls data source, watermarking, and LLM behaviour."""

    PRODUCTION = "production"
    STAGING = "staging"
    DEMO = "demo"
    LOCAL = "local"


class ReasoningModuleType(StrEnum):
    """The four production reasoning modules."""

    VARIANCE = "variance"
    DISCLOSURES = "disclosures"
    CONVERSATIONAL = "conversational"
    TRIAGE = "triage"


class ReviewOutcome(StrEnum):
    """Human review outcome for reasoning outputs destined for external use."""

    ACCEPTED = "accepted"
    EDITED = "edited"
    REJECTED = "rejected"


class WorkflowTaskStatus(StrEnum):
    """Close-calendar task status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETE = "complete"
    OVERDUE = "overdue"


class IRRBBShock(StrEnum):
    """The six standard interest rate shocks from the BCBS IRRBB standard (2016)."""

    PARALLEL_UP = "parallel_up"
    PARALLEL_DOWN = "parallel_down"
    STEEPENER = "steepener"
    FLATTENER = "flattener"
    SHORT_RATE_UP = "short_rate_up"
    SHORT_RATE_DOWN = "short_rate_down"
