"""
Alert / recommendation logic.

Owner note: same caveat as kpi_calculations.py -- this is Analytics and
Decision Logic Lead's deliverable per the workplan. This is a placeholder
implementing the workplan's own Table 9 ("Minimum Decision Logic to
Include") thresholds, so the dashboard has real alerts to render instead
of dummy data. Replace with Analytics Lead's version once it exists;
until then, every threshold below is either sourced directly from Table 9
or explicitly marked ASSUMPTION where Table 9 is silent. Confirm
ASSUMPTION values before treating this as production logic.
"""

from __future__ import annotations

# Sourced directly from workplan Table 9.
BED_OCC_WARNING_PCT = 85
BED_OCC_CRITICAL_PCT = 95
ICU_OCC_CRITICAL_PCT = 90
WAIT_TIME_WARNING_MIN = 120  # "above 2 hours"
RISK_SHARE_INCREASE_WARNING_PCT = 20  # "disease cases increase by 20% or more"

# ASSUMPTION -- workplan Table 9 says "doctor workload above safe threshold"
# without a number. Not defined anywhere else in the workplan either.
# Confirm with Analytics Lead before relying on this value.
WORKLOAD_WARNING_PCT = 90


def bed_occupancy_alerts(occupancy_pct: float | None, label: str = "Overall") -> list[dict]:
    if occupancy_pct is None:
        return []
    if occupancy_pct >= BED_OCC_CRITICAL_PCT:
        return [{
            "level": "critical",
            "area": "Bed Occupancy",
            "message": (
                f"{label} bed occupancy at {occupancy_pct}% (>= {BED_OCC_CRITICAL_PCT}%). "
                "Activate overflow beds and review admissions."
            ),
        }]
    if occupancy_pct >= BED_OCC_WARNING_PCT:
        return [{
            "level": "warning",
            "area": "Bed Occupancy",
            "message": (
                f"{label} bed occupancy at {occupancy_pct}% (>= {BED_OCC_WARNING_PCT}%). "
                "Start discharge planning and prepare overflow beds."
            ),
        }]
    return []


def icu_occupancy_alerts(icu_occupancy_pct: float | None) -> list[dict]:
    if icu_occupancy_pct is None:
        return []
    if icu_occupancy_pct >= ICU_OCC_CRITICAL_PCT:
        return [{
            "level": "critical",
            "area": "ICU Occupancy",
            "message": (
                f"ICU occupancy at {icu_occupancy_pct}% (>= {ICU_OCC_CRITICAL_PCT}%). "
                "Review referrals and critical care staffing."
            ),
        }]
    return []


def waiting_time_alerts(avg_wait_minutes: float | None, label: str = "Overall") -> list[dict]:
    if avg_wait_minutes is None:
        return []
    if avg_wait_minutes >= WAIT_TIME_WARNING_MIN:
        return [{
            "level": "warning",
            "area": "Waiting Time",
            "message": (
                f"{label} average waiting time is {avg_wait_minutes} min "
                f"(>= {WAIT_TIME_WARNING_MIN} min). Add another doctor or open "
                "another consultation point."
            ),
        }]
    return []


def workload_alerts(workload_pct: float | None, label: str = "Overall") -> list[dict]:
    if workload_pct is None:
        return []
    if workload_pct >= WORKLOAD_WARNING_PCT:
        return [{
            "level": "warning",
            "area": "Doctor Workload",
            "message": (
                f"{label} workload at {workload_pct}% (>= assumed threshold "
                f"{WORKLOAD_WARNING_PCT}%, unconfirmed). Reassign staff or "
                "call backup support."
            ),
        }]
    return []


def risk_trend_alerts(pct_change_vs_prior_month: float | None) -> list[dict]:
    """
    Proxy for Table 9's "disease cases increase by 20% or more".

    There is no diagnosis/disease field in this dataset -- see
    kpi_calculations.risk_trend(). This fires on month-over-month change in
    high-risk-patient share, not actual disease case counts. Label any UI
    alert built on this clearly as a risk-trend proxy, not a disease alert.
    """
    if pct_change_vs_prior_month is None:
        return []
    if pct_change_vs_prior_month >= RISK_SHARE_INCREASE_WARNING_PCT:
        return [{
            "level": "warning",
            "area": "Risk Trend (proxy for disease trend)",
            "message": (
                f"High-risk patient share up {pct_change_vs_prior_month}% "
                f"vs. prior month (>= {RISK_SHARE_INCREASE_WARNING_PCT}%). "
                "Prepare supplies and alert management."
            ),
        }]
    return []


def pharmacy_alerts() -> list[dict]:
    """
    Table 9: "Pharmacy delays exceed target". NOT IMPLEMENTED.

    waiting_times.csv has one aggregate waiting_time_mins per admission --
    no pharmacy-stage timestamp exists anywhere in the committed data.
    This cannot be computed without a schema change from Data Engineer.
    Returns [] rather than fabricating a number.
    """
    return []


def lab_alerts() -> list[dict]:
    """Table 9: "Lab turnaround exceeds target". NOT IMPLEMENTED -- same reason as pharmacy_alerts()."""
    return []


SEVERITY_ORDER = {"critical": 0, "warning": 1}


def sort_alerts(alerts: list[dict]) -> list[dict]:
    return sorted(alerts, key=lambda a: SEVERITY_ORDER.get(a["level"], 99))
