import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.data_utils import (
    load_beds,
    load_disease_trends,
    load_doctor_workload,
    load_waiting_times,
)
from src.decision_rules import (
    bed_occupancy_alerts,
    icu_occupancy_alerts,
    lab_alerts,
    pharmacy_alerts,
    risk_trend_alerts,
    sort_alerts,
    waiting_time_alerts,
    workload_alerts,
)
from src.kpi_calculations import (
    avg_waiting_time,
    bed_occupancy_by_ward,
    bed_occupancy_rate,
    doctor_workload_avg,
    overloaded_doctors,
    risk_trend,
    waiting_time_by_department,
)
from src.decision_rules import WORKLOAD_WARNING_PCT

st.set_page_config(page_title="Recommendations", layout="wide")
st.title("Recommendations")
st.caption(
    "Priority levels: critical = act now, warning = plan action this week. "
    "Every recommendation below is a direct consequence of a Table 9 "
    "threshold in the project workplan -- see src/decision_rules.py for "
    "exact values and which ones are still unconfirmed assumptions."
)

beds_df = load_beds()
waiting_df = load_waiting_times()
doctor_df = load_doctor_workload()
disease_df = load_disease_trends()

overall_occ = bed_occupancy_rate(beds_df)
icu_occ = bed_occupancy_rate(beds_df, ward_name="ICU")
ward_df = bed_occupancy_by_ward(beds_df)
avg_wait = avg_waiting_time(waiting_df)
wait_by_dept = waiting_time_by_department(waiting_df)
overloaded = overloaded_doctors(doctor_df, WORKLOAD_WARNING_PCT)
risk_df = risk_trend(disease_df)
latest_change = risk_df["pct_change_vs_prior_month"].iloc[-1] if len(risk_df) > 1 else None

alerts = []
alerts += bed_occupancy_alerts(overall_occ)
alerts += icu_occupancy_alerts(icu_occ)
for row in ward_df.itertuples():
    alerts += bed_occupancy_alerts(row.occupancy_pct, label=row.ward_name)
alerts += waiting_time_alerts(avg_wait)
for row in wait_by_dept.itertuples():
    alerts += waiting_time_alerts(row.avg_waiting_time_mins, label=row.department)
for _, row in overloaded.iterrows():
    alerts += workload_alerts(row["workload_pct"], label=row["doctor_name"])
alerts += risk_trend_alerts(latest_change)
alerts += pharmacy_alerts()
alerts += lab_alerts()
alerts = sort_alerts(alerts)

critical = [a for a in alerts if a["level"] == "critical"]
warning = [a for a in alerts if a["level"] == "warning"]

c1, c2 = st.columns(2)
c1.metric("Critical", len(critical))
c2.metric("Warning", len(warning))

st.divider()

if critical:
    st.subheader("Critical")
    for a in critical:
        st.error(f"**{a['area']}** -- {a['message']}")

if warning:
    st.subheader("Warning")
    for a in warning:
        st.warning(f"**{a['area']}** -- {a['message']}")

if not alerts:
    st.success("No threshold breaches on the current snapshot.")

st.divider()
st.subheader("Not Implemented (data doesn't support these Table 9 rules)")
st.info(
    "- Pharmacy delays exceed target -- no pharmacy-stage timestamp in the data.\n"
    "- Lab turnaround exceeds target -- no lab-stage timestamp in the data.\n\n"
    "Both need a schema change from Data Engineer (per-stage timing in "
    "waiting_times.csv or a new source table) before they can be built."
)
