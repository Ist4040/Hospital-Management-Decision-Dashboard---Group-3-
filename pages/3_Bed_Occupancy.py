import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.express as px
import streamlit as st

from src.data_utils import load_beds
from src.decision_rules import bed_occupancy_alerts, icu_occupancy_alerts, sort_alerts
from src.kpi_calculations import bed_occupancy_by_ward, bed_occupancy_rate

st.set_page_config(page_title="Bed Occupancy", layout="wide")
st.title("Bed Occupancy")
st.caption(
    "beds.csv is a single point-in-time snapshot (no timestamp column). "
    "These numbers are current state, not a trend over time."
)

beds_df = load_beds()
ward_df = bed_occupancy_by_ward(beds_df)

overall_occ = bed_occupancy_rate(beds_df)
icu_occ = bed_occupancy_rate(beds_df, ward_name="ICU")

c1, c2, c3 = st.columns(3)
c1.metric("Total Beds", f"{len(beds_df):,}")
c2.metric("Occupied Beds", f"{int(beds_df['is_occupied'].sum()):,}")
c3.metric("Overall Occupancy", f"{overall_occ}%" if overall_occ is not None else "N/A")

st.divider()

col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Occupancy by Ward")
    st.plotly_chart(
        px.bar(ward_df, x="ward_name", y="occupancy_pct", range_y=[0, 100]),
        use_container_width=True,
    )
with col_right:
    st.subheader("Ward Detail")
    st.dataframe(ward_df, use_container_width=True)

st.divider()
st.subheader("Alerts")
alerts = sort_alerts(bed_occupancy_alerts(overall_occ) + icu_occupancy_alerts(icu_occ))
for row in ward_df.itertuples():
    alerts.extend(bed_occupancy_alerts(row.occupancy_pct, label=row.ward_name))
alerts = sort_alerts(alerts)

if not alerts:
    st.success("No occupancy threshold breaches on the current snapshot.")
else:
    for a in alerts:
        renderer = st.error if a["level"] == "critical" else st.warning
        renderer(f"**{a['area']}** -- {a['message']}")
