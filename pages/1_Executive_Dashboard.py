import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.express as px
import streamlit as st

from src.data_utils import (
    load_admissions,
    load_beds,
    load_disease_trends,
    load_doctor_workload,
    load_waiting_times,
)
from src.decision_rules import (
    bed_occupancy_alerts,
    icu_occupancy_alerts,
    risk_trend_alerts,
    sort_alerts,
    waiting_time_alerts,
    workload_alerts,
)
from src.kpi_calculations import (
    admissions_by_department,
    avg_waiting_time,
    bed_occupancy_rate,
    doctor_workload_avg,
    risk_trend,
    total_admissions,
)

st.set_page_config(page_title="Executive Dashboard", layout="wide")
st.title("Executive Dashboard")

beds_df = load_beds()
admissions_df = load_admissions()
waiting_df = load_waiting_times()
doctor_df = load_doctor_workload()
disease_df = load_disease_trends()

overall_occ = bed_occupancy_rate(beds_df)
icu_occ = bed_occupancy_rate(beds_df, ward_name="ICU")
admissions_count = total_admissions(admissions_df)
avg_wait = avg_waiting_time(waiting_df)
workload_avg = doctor_workload_avg(doctor_df)
risk_df = risk_trend(disease_df)
latest_risk_change = (
    risk_df["pct_change_vs_prior_month"].iloc[-1] if len(risk_df) > 1 else None
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Bed Occupancy", f"{overall_occ}%" if overall_occ is not None else "N/A")
c2.metric("ICU Occupancy", f"{icu_occ}%" if icu_occ is not None else "N/A")
c3.metric("Total Admissions", f"{admissions_count:,}")
c4.metric("Avg Waiting Time", f"{avg_wait} min" if avg_wait is not None else "N/A")
c5.metric("Avg Doctor Workload", f"{workload_avg}%" if workload_avg is not None else "N/A")

st.divider()

col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Admissions by Department")
    dept_df = admissions_by_department(admissions_df)
    st.plotly_chart(px.bar(dept_df, x="department", y="admissions"), use_container_width=True)

with col_right:
    st.subheader("Risk Trend (proxy -- see caption)")
    st.plotly_chart(
        px.line(risk_df, x="month_year", y="high_risk_share_pct", markers=True),
        use_container_width=True,
    )
    st.caption(
        "No diagnosis field exists in this dataset -- this tracks high-risk "
        "patient share, not disease-specific trends."
    )

st.divider()
st.subheader("Active Alerts (all areas)")

alerts = sort_alerts(
    bed_occupancy_alerts(overall_occ)
    + icu_occupancy_alerts(icu_occ)
    + waiting_time_alerts(avg_wait)
    + workload_alerts(workload_avg)
    + risk_trend_alerts(latest_risk_change)
)

if not alerts:
    st.success("No threshold breaches on the current snapshot.")
else:
    for a in alerts:
        renderer = st.error if a["level"] == "critical" else st.warning
        renderer(f"**{a['area']}** -- {a['message']}")
