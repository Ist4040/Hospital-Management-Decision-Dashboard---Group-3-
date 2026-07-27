# Dashboard Wireframe / Page Spec

Owner: Member 4 (Dashboard Developer and UI Lead). Scoped against the
CSVs actually committed to `main` as of 2026-07-27, not against the
workplan's page descriptions verbatim -- three of the workplan's page
specs describe content the current data cannot produce. Those gaps are
called out explicitly per page below. This doc should be shared with
Project Lead and Analytics Lead before further build-out, since two of
the gaps require Data Engineer to change the source schema, not just a
UI decision.

## Global

- Navigation: Streamlit native multipage (`pages/` directory, auto
  sidebar). `app.py` is Home.
- Every page reads from `src/data_utils.py`, never from
  `src/data_loader.py` directly (that module crashes on import if the raw
  `.xlsx` isn't present -- see comment block at the top of `data_utils.py`).
- Alert thresholds live in one place: `src/decision_rules.py`. Pages call
  functions from there; no page hardcodes a threshold number itself. When
  Analytics Lead delivers their own `decision_rules.py`, only that one
  file needs to change.
- Data is a static snapshot (CSVs generated once from a source Excel
  file), not a live feed. Every page should make this visible to the
  user via a caption, not imply real-time data.

## 1. Executive Dashboard (`pages/1_Executive_Dashboard.py`)

KPI cards: bed occupancy (overall + ICU), total admissions, average
waiting time, average doctor workload. Admissions-by-department bar
chart. Risk trend line chart (see Disease Trends gap below). Combined
alert feed across all rule areas.

Status: built.

## 2. Patient Admissions (`pages/2_Patient_Admissions.py`)

Daily admissions trend, admissions by department, peak admission hour
(admission_date includes time-of-day, verified against real data --
hour-level analysis is valid). Department filter.

**Gap:** workplan spec says "emergency vs outpatient cases." The
`department` field has 4 values (ICU, General Ward, Emergency Room, HDU)
-- no Outpatient category exists in this data. Built as "Emergency Room
share" instead. If Outpatient tracking matters for the grade, Data
Engineer needs to add it as a department value or a separate flag.

Status: built.

## 3. Bed Occupancy (`pages/3_Bed_Occupancy.py`)

Total/occupied/available beds, occupancy by ward, ICU-specific occupancy,
threshold alerts (85% warning / 95% critical per Table 9).

**Gap:** `beds.csv` has no timestamp column -- it's a single snapshot.
Occupancy is a current-state number, not a trend line. Don't build a
"bed occupancy over time" chart; the data can't back it.

Status: built.

## 4. Waiting Times (`pages/4_Waiting_Times.py`)

Average wait by department, wait time distribution, department filter,
threshold alert (>= 120 min per Table 9).

**Gap -- the largest one:** the workplan wants registration, triage,
consultation, lab, pharmacy, and discharge wait times broken out
separately, with per-stage bottleneck alerts. `waiting_times.csv` has
exactly one column, `waiting_time_mins`, aggregated per admission. There
is no stage-level timestamp anywhere in the committed data. This page
shows total wait time only. Table 9's "pharmacy delays" and "lab
turnaround" alerts are explicitly stubbed as not-implemented in
`decision_rules.py` rather than faked. **Needs a decision from Data
Engineer / Project Lead:** either the raw Excel source has stage-level
timestamps that weren't carried into the CSV export, or it doesn't exist
at all and this page's scope needs to be formally reduced before grading.

Status: built, scope-reduced.

## 5. Doctor Workload (`pages/5_Doctor_Workload.py`)

Average workload by specialty, workload distribution, shift filter, list
of doctors over threshold, threshold alert.

**Open item:** "doctor workload above safe threshold" in Table 9 has no
number attached anywhere in the workplan. Built using an assumed 90%
(matching the ICU occupancy threshold pattern), clearly marked
"unconfirmed" in the UI and in code comments. **Needs Analytics Lead to
confirm or override this number.**

Status: built, threshold unconfirmed.

## 6. Disease Trends (`pages/6_Disease_Trends.py`)

**Gap -- second largest:** there is no diagnosis or disease-name field
anywhere in this dataset (not in `admissions.csv`, not in
`disease_trends.csv`). "Top diseases" and per-disease outbreak
detection, as specified in the workplan, cannot be built from what's
committed. Built the closest real substitute: monthly admission volume,
high-risk-patient share (>= 2 chronic conditions, from
`patient_demographics.csv`), and month-over-month change in that share,
used as a proxy for Table 9's "disease cases increase by 20%" rule. Page
and code label this explicitly as a proxy, not a disease trend, to avoid
presenting a metric as something it isn't. **If the assignment grades
against the literal "top diseases" spec, this page will not satisfy it
without a real diagnosis field added to the data.**

Status: built, scope substantially reduced, needs a call from Project
Lead on whether this is acceptable or the data needs to change.

## 7. Recommendations (`pages/7_Recommendations.py`)

Aggregated alert feed across all rule areas, split by critical/warning,
plus an explicit "not implemented" section listing the two Table 9 rules
(pharmacy delay, lab turnaround) that the current data cannot support.

Status: built.

## Screenshots

Not started. Capture after Analytics Lead's real `kpi_calculations.py` /
`decision_rules.py` land and replace the placeholders above -- screenshots
taken against placeholder thresholds will need to be retaken if the
numbers change, so sequence this last.

## Summary of open items blocking "final" status

1. Analytics Lead needs to deliver real `kpi_calculations.py` /
   `decision_rules.py`, or explicitly sign off on the placeholder versions
   in `src/` as final.
2. Doctor workload "safe threshold" needs a real number.
3. Waiting-times per-stage breakdown: confirm whether the raw source data
   has it and it was dropped in the CSV export, or it was never captured.
4. Disease trends: confirm whether "top diseases" is a hard requirement.
   If so, a diagnosis field needs to be added to the dataset.
5. `docs/data_dictionary.md` needs `patient_demographics.csv` added --
   currently undocumented (columns: patient_id, age, gender,
   chronic_conditions_count, risk_segment, reverse-engineered from
   `src/data_loader.py`, not from a written contract).
