"""
Hospital Management Decision Support System -- entry point / Home page.

Run with: streamlit run app.py
Requires: pip install -r requirements.txt

Page navigation is Streamlit's native multipage convention -- every file
in pages/ appears automatically in the sidebar. No manual routing needed.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.data_utils import load_beds, load_admissions, load_doctor_workload
from src.kpi_calculations import bed_occupancy_rate, doctor_workload_avg
from src.decision_rules import bed_occupancy_alerts, workload_alerts, sort_alerts

st.set_page_config(
    page_title="Hospital Management DSS",
    page_icon="🏥",
    layout="wide",
)

st.title("Hospital Management Decision Support System")
st.caption(
    "Sample-data dashboard for admissions, bed occupancy, waiting times, "
    "doctor workload, and risk trends. Data is a static snapshot, not a "
    "live feed -- see docs/data_dictionary.md for source and refresh notes."
)

st.markdown("Use the sidebar to open a dashboard page. Quick snapshot below.")

try:
    beds_df = load_beds()
    admissions_df = load_admissions()
    doctor_df = load_doctor_workload()
except FileNotFoundError as e:
    st.error(f"Could not load data: {e}")
    st.stop()

occ = bed_occupancy_rate(beds_df)
workload = doctor_workload_avg(doctor_df)

col1, col2, col3 = st.columns(3)
col1.metric("Overall Bed Occupancy", f"{occ}%" if occ is not None else "N/A")
col2.metric("Total Admissions (all-time)", f"{len(admissions_df):,}")
col3.metric("Avg Doctor Workload", f"{workload}%" if workload is not None else "N/A")

alerts = sort_alerts(bed_occupancy_alerts(occ) + workload_alerts(workload))

st.subheader("Active Alerts")
if not alerts:
    st.success("No threshold breaches on the current snapshot.")
else:
    for a in alerts:
        if a["level"] == "critical":
            st.error(f"**{a['area']}** -- {a['message']}")
        else:
            st.warning(f"**{a['area']}** -- {a['message']}")

st.divider()
st.caption(
    "Alert thresholds are sourced from the project workplan (Table 9) "
    "pending final sign-off from Analytics Lead. See src/decision_rules.py "
    "for exact values and open assumptions."
)
