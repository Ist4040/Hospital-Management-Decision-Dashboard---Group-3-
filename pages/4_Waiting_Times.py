import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.express as px
import streamlit as st

from src.data_utils import load_waiting_times
from src.decision_rules import sort_alerts, waiting_time_alerts
from src.kpi_calculations import avg_waiting_time, waiting_time_by_department

st.set_page_config(page_title="Waiting Times", layout="wide")
st.title("Waiting Times")

st.warning(
    "**Scope note:** waiting_times.csv has one aggregate `waiting_time_mins` "
    "per admission -- there is no registration/triage/consultation/lab/"
    "pharmacy/discharge breakdown in the committed data, even though the "
    "workplan's page spec calls for per-stage bottleneck detection. This "
    "page shows total wait time only. Per-stage view needs a schema change "
    "from Data Engineer before it can be built truthfully."
)

waiting_df = load_waiting_times()

departments = ["All"] + sorted(waiting_df["department"].dropna().unique().tolist())
selected_dept = st.sidebar.selectbox("Department", departments)
df = waiting_df if selected_dept == "All" else waiting_df[waiting_df["department"] == selected_dept]

avg_wait = avg_waiting_time(df)
c1, c2 = st.columns(2)
c1.metric("Average Wait (filtered)", f"{avg_wait} min" if avg_wait is not None else "N/A")
c2.metric("Admissions Counted", f"{len(df):,}")

st.divider()

col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Average Wait by Department")
    dept_df = waiting_time_by_department(waiting_df)
    st.plotly_chart(
        px.bar(dept_df, x="department", y="avg_waiting_time_mins"), use_container_width=True
    )
with col_right:
    st.subheader("Wait Time Distribution (filtered)")
    st.plotly_chart(px.histogram(df, x="waiting_time_mins", nbins=30), use_container_width=True)

st.divider()
st.subheader("Alerts")
alerts = sort_alerts(waiting_time_alerts(avg_wait, label=selected_dept))
for row in waiting_time_by_department(waiting_df).itertuples():
    alerts.extend(waiting_time_alerts(row.avg_waiting_time_mins, label=row.department))
alerts = sort_alerts(alerts)

if not alerts:
    st.success("No waiting-time threshold breaches on the current snapshot.")
else:
    for a in alerts:
        renderer = st.error if a["level"] == "critical" else st.warning
        renderer(f"**{a['area']}** -- {a['message']}")
