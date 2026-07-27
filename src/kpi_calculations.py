"""
KPI aggregation functions.

Owner note: this file exists in the Dashboard Developer's scope only as a
placeholder to unblock UI work. Per the 4-week workplan, KPI definitions
are Analytics and Decision Logic Lead's deliverable (kpi_calculations.py
is explicitly listed as their file). If Analytics Lead ships a real
version of this file, replace this one -- don't silently maintain two
KPI definitions that can drift apart.

Every function below is a straightforward aggregate with no hidden
business logic. Where a formula choice was ambiguous (e.g. "average
waiting time" -- overall vs. per department vs. rolling window), the
default is documented in the docstring. Confirm defaults with Analytics
Lead before treating any of these as final.
"""

from __future__ import annotations

import pandas as pd


def bed_occupancy_rate(beds_df: pd.DataFrame, ward_name: str | None = None) -> float | None:
    """Current occupied/total beds, as a percentage. None if no beds match."""
    df = beds_df if ward_name is None else beds_df[beds_df["ward_name"] == ward_name]
    if len(df) == 0:
        return None
    return round(df["is_occupied"].sum() / len(df) * 100, 1)


def bed_occupancy_by_ward(beds_df: pd.DataFrame) -> pd.DataFrame:
    grouped = beds_df.groupby("ward_name").agg(
        total_beds=("bed_id", "count"),
        occupied_beds=("is_occupied", "sum"),
    )
    grouped["occupancy_pct"] = (grouped["occupied_beds"] / grouped["total_beds"] * 100).round(1)
    return grouped.reset_index()


def total_admissions(admissions_df: pd.DataFrame, start=None, end=None) -> int:
    """Count of admissions. Optionally bounded by admission_date range."""
    df = admissions_df
    if start is not None:
        df = df[df["admission_date"] >= start]
    if end is not None:
        df = df[df["admission_date"] <= end]
    return int(len(df))


def admissions_by_department(admissions_df: pd.DataFrame) -> pd.DataFrame:
    return (
        admissions_df.groupby("department")["admission_id"]
        .count()
        .reset_index(name="admissions")
        .sort_values("admissions", ascending=False)
    )


def admissions_by_hour(admissions_df: pd.DataFrame) -> pd.DataFrame:
    """Peak admission time-of-day. admission_date carries HH:MM:SS, verified 2026-07-27."""
    hours = admissions_df["admission_date"].dt.hour
    counts = hours.value_counts().sort_index().reset_index()
    # Column-name-by-position, not by assumed label: pandas' reset_index()
    # label for the index column varies across versions depending on
    # whether the source Series carries a name. Don't rely on "index".
    counts.columns = ["hour", "admissions"]
    return counts


def emergency_share_pct(admissions_df: pd.DataFrame) -> float | None:
    """
    Share of admissions in the 'Emergency Room' department.

    Named emergency_share, not emergency_vs_outpatient: this dataset's
    `department` field has 4 values (ICU, General Ward, Emergency Room,
    HDU) with no 'Outpatient' category. Don't build an emergency-vs-
    outpatient chart -- the category doesn't exist in the data.
    """
    if len(admissions_df) == 0:
        return None
    return round((admissions_df["department"] == "Emergency Room").mean() * 100, 1)


def avg_waiting_time(waiting_df: pd.DataFrame, department: str | None = None) -> float | None:
    df = waiting_df if department is None else waiting_df[waiting_df["department"] == department]
    if len(df) == 0 or df["waiting_time_mins"].isna().all():
        return None
    return round(df["waiting_time_mins"].mean(), 1)


def waiting_time_by_department(waiting_df: pd.DataFrame) -> pd.DataFrame:
    return (
        waiting_df.groupby("department")["waiting_time_mins"]
        .mean()
        .round(1)
        .reset_index(name="avg_waiting_time_mins")
        .sort_values("avg_waiting_time_mins", ascending=False)
    )


def doctor_workload_avg(doctor_df: pd.DataFrame, specialty: str | None = None) -> float | None:
    df = doctor_df if specialty is None else doctor_df[doctor_df["specialty"] == specialty]
    if len(df) == 0:
        return None
    return round(df["workload_pct"].mean(), 1)


def workload_by_specialty(doctor_df: pd.DataFrame) -> pd.DataFrame:
    return (
        doctor_df.groupby("specialty")["workload_pct"]
        .mean()
        .round(1)
        .reset_index(name="avg_workload_pct")
        .sort_values("avg_workload_pct", ascending=False)
    )


def overloaded_doctors(doctor_df: pd.DataFrame, threshold_pct: float) -> pd.DataFrame:
    return doctor_df[doctor_df["workload_pct"] >= threshold_pct].sort_values(
        "workload_pct", ascending=False
    )


def risk_trend(disease_df: pd.DataFrame) -> pd.DataFrame:
    """
    Monthly high-risk-patient share, with month-over-month percentage change.

    This is a proxy metric, not a disease/diagnosis trend. disease_trends.csv
    has no diagnosis field -- see module docstring in data_utils.py. Label
    any UI built on this as "risk trend", not "top diseases" or "disease
    trends", or the page is showing data it doesn't have.
    """
    df = disease_df.copy()
    df["high_risk_share_pct"] = (df["high_risk_patients"] / df["total_admissions"] * 100).round(1)
    df["pct_change_vs_prior_month"] = df["high_risk_share_pct"].pct_change().mul(100).round(1)
    return df


def patient_risk_summary(patient_df: pd.DataFrame) -> pd.DataFrame:
    return (
        patient_df.groupby("risk_segment")["patient_id"]
        .count()
        .reset_index(name="patient_count")
    )
