Draft for Gambino to send to the team (Project Lead, Data Engineer,
Analytics Lead). Edit before sending -- this is a starting point, not a
finished message.

---

Status update from Dashboard Developer / UI Lead.

I've built out `app.py` and all 7 pages (`pages/1_Executive_Dashboard.py`
through `pages/7_Recommendations.py`), plus `requirements.txt` and a new
`src/data_utils.py` for loading the CSVs. Wiring notes and a full page-by-
page spec are in `docs/dashboard_wireframe.md`. Five things need input
before I'd call this done:

**1. `src/data_loader.py` has a bug that will break deployment.**
It raises `FileNotFoundError` at import time if the raw `.xlsx` source
file isn't present. That file is `.gitignore`'d and isn't in the repo, so
importing `data_loader.py` from anywhere -- including just to read the
already-committed CSVs -- crashes immediately on a fresh clone or on
Streamlit Community Cloud. I've worked around it by adding
`src/data_utils.py`, which reads `data/*.csv` directly and never touches
`data_loader.py`. Data Engineer: worth moving the file-existence check
inside `load_and_process_data()` so the module is safe to import even
when nobody's regenerating data from the raw Excel.

**2. No `kpi_calculations.py` or `decision_rules.py` existed yet**, so I
wrote placeholder versions to unblock the dashboard build. The
thresholds in `decision_rules.py` are pulled directly from the
workplan's Table 9, with one gap: "doctor workload above safe threshold"
has no number anywhere in the workplan. I used 90% as a placeholder,
marked unconfirmed in the UI. Analytics Lead -- when your real versions
are ready, they can drop in and replace mine; I kept the KPI/rule logic
isolated in `src/` specifically so this swap doesn't touch any page code.
If 90% isn't right, tell me and I'll fix it in one place.

**3. Waiting Times page is scope-reduced.** `waiting_times.csv` only has
one aggregate `waiting_time_mins` per admission -- no
registration/triage/consultation/lab/pharmacy/discharge breakdown. The
workplan's spec and Table 9's pharmacy/lab alerts assume that breakdown
exists. It doesn't, in what's committed. Does the raw Excel source have
stage-level timestamps that got dropped during CSV export, or was it
never captured? If it's recoverable, I'd rather have real data than fake
columns.

**4. Disease Trends page had to change scope more substantially.** There
is no diagnosis or disease-name field anywhere in the dataset -- not in
`admissions.csv`, not in `disease_trends.csv`. I can't build "top
diseases" or per-disease outbreak alerts from what exists. I built the
closest real substitute (high-risk-patient-share trend, from chronic
condition counts) and labeled it clearly as a proxy rather than
pretending it's disease data. If "top diseases" is a hard requirement
for grading, we need an actual diagnosis field added to the dataset --
that's a data change, not something I can UI my way around.

**5. `docs/data_dictionary.md` is missing `patient_demographics.csv`.**
It documents 5 files; the repo has 6. I reverse-engineered the columns
(patient_id, age, gender, chronic_conditions_count, risk_segment) from
`data_loader.py`'s write step to build the dashboard, but that's not a
substitute for it being documented properly.

None of this blocks a working demo -- the dashboard runs end to end
against what's actually in the data right now. It does mean items 3 and
4 will look different from the original page spec unless we get data
changes, so flagging now instead of at Week 4.
