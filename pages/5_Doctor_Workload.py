import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.express as px
import streamlit as st

from src.data_utils import load_doctor_workload
from src.decision_rules import WORKLOAD_WARNING_PCT, sort_alerts, workload_alerts
from src.kpi_calculations import doctor_workload_avg, overloaded_doctors, workload_by_specialty

st.set_page_config(page_title="Doctor Workload", layout="wide")
st.title("Doctor Workload")

doctor_df = load_doctor_workload()

shifts = ["All"] + sorted(doctor_df["assigned_shift"].dropna().unique().tolist())
selected_shift = st.sidebar.selectbox("Shift", shifts)
df = doctor_df if selected_shift == "All" else doctor_df[doctor_df["assigned_shift"] == selected_shift]

avg_workload = doctor_workload_avg(df)
c1, c2 = st.columns(2)
c1.metric("Avg Workload (filtered)", f"{avg_workload}%" if avg_workload is not None else "N/A")
c2.metric("Doctors Counted", f"{len(df):,}")

st.divider()

col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Avg Workload by Specialty")
    spec_df = workload_by_specialty(df)
    st.plotly_chart(px.bar(spec_df, x="specialty", y="avg_workload_pct"), use_container_width=True)
with col_right:
    st.subheader("Workload Distribution")
    st.plotly_chart(px.histogram(df, x="workload_pct", nbins=20), use_container_width=True)

st.divider()
st.subheader(f"Overloaded Doctors (>= {WORKLOAD_WARNING_PCT}%, unconfirmed threshold)")
overloaded = overloaded_doctors(df, WORKLOAD_WARNING_PCT)
if len(overloaded) == 0:
    st.success("No doctors above the assumed workload threshold.")
else:
    st.dataframe(
        overloaded[["doctor_name", "specialty", "assigned_shift", "workload_pct"]],
        use_container_width=True,
    )

st.divider()
st.subheader("Alerts")
alerts = sort_alerts([
    a for _, row in overloaded.iterrows()
    for a in workload_alerts(row["workload_pct"], label=row["doctor_name"])
])
if not alerts:
    st.success("No workload threshold breaches on the current snapshot.")
else:
    for a in alerts:
        renderer = st.error if a["level"] == "critical" else st.warning
        renderer(f"**{a['area']}** -- {a['message']}")
