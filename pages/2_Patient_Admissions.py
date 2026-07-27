import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.express as px
import streamlit as st

from src.data_utils import load_admissions
from src.kpi_calculations import admissions_by_department, admissions_by_hour, emergency_share_pct

st.set_page_config(page_title="Patient Admissions", layout="wide")
st.title("Patient Admissions")

admissions_df = load_admissions()

departments = ["All"] + sorted(admissions_df["department"].dropna().unique().tolist())
selected_dept = st.sidebar.selectbox("Department", departments)

df = admissions_df if selected_dept == "All" else admissions_df[admissions_df["department"] == selected_dept]

c1, c2 = st.columns(2)
c1.metric("Admissions (filtered)", f"{len(df):,}")
er_share = emergency_share_pct(admissions_df)
c2.metric("Emergency Room Share (all departments)", f"{er_share}%" if er_share is not None else "N/A")
st.caption(
    "Department values in this dataset: ICU, General Ward, Emergency Room, HDU. "
    "There is no 'Outpatient' category, so an emergency-vs-outpatient split "
    "isn't derivable -- Emergency Room share is shown instead."
)

st.divider()

col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Daily Admissions")
    daily = df.groupby(df["admission_date"].dt.date)["admission_id"].count().reset_index(
        name="admissions"
    )
    daily.columns = ["date", "admissions"]
    st.plotly_chart(px.line(daily, x="date", y="admissions"), use_container_width=True)

with col_right:
    st.subheader("Admissions by Department")
    dept_df = admissions_by_department(df)
    st.plotly_chart(px.bar(dept_df, x="department", y="admissions"), use_container_width=True)

st.subheader("Peak Admission Times (hour of day)")
hour_df = admissions_by_hour(df)
st.plotly_chart(px.bar(hour_df, x="hour", y="admissions"), use_container_width=True)

with st.expander("Raw admissions data (filtered)"):
    st.dataframe(df, use_container_width=True)
