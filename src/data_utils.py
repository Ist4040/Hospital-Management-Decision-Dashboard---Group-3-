"""
Data loading layer for the dashboard.

Deliberately does NOT import from src/data_loader.py. That module raises
FileNotFoundError at MODULE IMPORT TIME if a raw .xlsx source file is
missing (see its top-level code). The .xlsx is .gitignore'd and is not
committed to this repo, so any code that imports data_loader.py will crash
on import in a fresh clone or on Streamlit Community Cloud -- even if all
you want is to read the already-committed CSVs in data/.

This module reads data/*.csv directly. It has no import-time side effects:
every check happens inside a function, only when that function is called.

Known data limitations (verified against the committed CSVs as of
2026-07-27 -- confirm these are still accurate before relying on them):

- waiting_times.csv has ONE aggregate `waiting_time_mins` per admission.
  There is no per-stage breakdown (registration/triage/consultation/lab/
  pharmacy/discharge). Do not fabricate stage-level numbers from this file.
- disease_trends.csv has NO diagnosis/disease-name column anywhere. It is
  monthly admission volume + chronic-condition risk aggregates
  (total_admissions, high_risk_patients, avg_chronic_conditions). There is
  no way to show "top diseases" from this dataset as it currently exists.
- beds.csv is a single point-in-time snapshot (no timestamp column). You
  can compute current occupancy, not an occupancy trend over time.
- department values observed in admissions.csv: ICU, General Ward,
  Emergency Room, HDU. There is no "Outpatient" category in this data.
- admission_date / discharge_date DO include a time-of-day component
  (YYYY-MM-DD HH:MM:SS), so hour-of-day / peak-admission-time analysis is
  supported.
- patient_demographics.csv columns (undocumented in docs/data_dictionary.md
  as of this writing): patient_id, age, gender, chronic_conditions_count,
  risk_segment. Get the data dictionary updated -- this was reverse
  engineered from src/data_loader.py's write step, not from a contract.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _read_csv(filename: str, **kwargs) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Expected data file not found: {path}. "
            f"Confirm data/{filename} is committed to the repo."
        )
    return pd.read_csv(path, **kwargs)


@st.cache_data(ttl=3600)
def load_admissions() -> pd.DataFrame:
    df = _read_csv("admissions.csv")
    df["admission_date"] = pd.to_datetime(df["admission_date"], errors="coerce")
    df["discharge_date"] = pd.to_datetime(df["discharge_date"], errors="coerce")
    df["waiting_time_mins"] = pd.to_numeric(df["waiting_time_mins"], errors="coerce")
    df["severity_score"] = pd.to_numeric(df["severity_score"], errors="coerce")
    df["length_of_stay_days"] = pd.to_numeric(df["length_of_stay_days"], errors="coerce")
    return df


@st.cache_data(ttl=3600)
def load_beds() -> pd.DataFrame:
    df = _read_csv("beds.csv")
    df["is_occupied"] = pd.to_numeric(df["is_occupied"], errors="coerce").fillna(0).astype(int)
    return df


@st.cache_data(ttl=3600)
def load_waiting_times() -> pd.DataFrame:
    df = _read_csv("waiting_times.csv")
    df["admission_date"] = pd.to_datetime(df["admission_date"], errors="coerce")
    df["waiting_time_mins"] = pd.to_numeric(df["waiting_time_mins"], errors="coerce")
    return df


@st.cache_data(ttl=3600)
def load_doctor_workload() -> pd.DataFrame:
    df = _read_csv("doctor_workload.csv")
    df["max_capacity"] = pd.to_numeric(df["max_capacity"], errors="coerce")
    df["active_patients"] = pd.to_numeric(df["active_patients"], errors="coerce")
    df["workload_pct"] = pd.to_numeric(df["workload_pct"], errors="coerce")
    return df


@st.cache_data(ttl=3600)
def load_disease_trends() -> pd.DataFrame:
    df = _read_csv("disease_trends.csv")
    df["total_admissions"] = pd.to_numeric(df["total_admissions"], errors="coerce")
    df["high_risk_patients"] = pd.to_numeric(df["high_risk_patients"], errors="coerce")
    df["avg_chronic_conditions"] = pd.to_numeric(df["avg_chronic_conditions"], errors="coerce")
    df = df.sort_values("month_year").reset_index(drop=True)
    return df


@st.cache_data(ttl=3600)
def load_patient_demographics() -> pd.DataFrame:
    df = _read_csv("patient_demographics.csv")
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["chronic_conditions_count"] = pd.to_numeric(df["chronic_conditions_count"], errors="coerce")
    return df
