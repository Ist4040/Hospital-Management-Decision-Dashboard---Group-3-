import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.express as px
import streamlit as st

from src.data_utils import load_disease_trends, load_patient_demographics
from src.decision_rules import risk_trend_alerts, sort_alerts
from src.kpi_calculations import patient_risk_summary, risk_trend

st.set_page_config(page_title="Disease Trends", layout="wide")
st.title("Disease Trends")

st.warning(
    "**Scope note:** this dataset has no diagnosis/disease-name field "
    "anywhere -- not in admissions.csv, not in disease_trends.csv. "
    "'Top diseases' and per-disease outbreak detection, as specified in "
    "the workplan, are not buildable from the committed data. This page "
    "shows the closest real proxy: monthly admission volume and "
    "high-risk-patient share (>= 2 chronic conditions), sourced from "
    "disease_trends.csv and patient_demographics.csv. Treat titles/labels "
    "below as 'risk trend', not 'disease trend', when presenting this."
)

disease_df = load_disease_trends()
patient_df = load_patient_demographics()

risk_df = risk_trend(disease_df)
latest_change = risk_df["pct_change_vs_prior_month"].iloc[-1] if len(risk_df) > 1 else None

c1, c2, c3 = st.columns(3)
c1.metric("Latest Month Admissions", f"{int(risk_df['total_admissions'].iloc[-1]):,}" if len(risk_df) else "N/A")
c2.metric(
    "Latest High-Risk Share",
    f"{risk_df['high_risk_share_pct'].iloc[-1]}%" if len(risk_df) else "N/A",
)
c3.metric(
    "MoM Change in High-Risk Share",
    f"{latest_change}%" if latest_change is not None else "N/A",
)

st.divider()

col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Admissions Over Time")
    st.plotly_chart(px.line(risk_df, x="month_year", y="total_admissions", markers=True), use_container_width=True)
with col_right:
    st.subheader("High-Risk Patient Share Over Time")
    st.plotly_chart(
        px.line(risk_df, x="month_year", y="high_risk_share_pct", markers=True),
        use_container_width=True,
    )

st.subheader("Patient Risk Segmentation (current snapshot)")
seg_df = patient_risk_summary(patient_df)
st.plotly_chart(px.pie(seg_df, names="risk_segment", values="patient_count"), use_container_width=True)

st.divider()
st.subheader("Alerts")
alerts = sort_alerts(risk_trend_alerts(latest_change))
if not alerts:
    st.success("No risk-trend threshold breaches on the current snapshot.")
else:
    for a in alerts:
        renderer = st.error if a["level"] == "critical" else st.warning
        renderer(f"**{a['area']}** -- {a['message']}")
