"""AI Report generation package — Epic 4C."""

from .base import Report, ReportType
from .generators import generate_report

__all__ = ["Report", "ReportType", "generate_report"]
