# Hospital DSS Data Dictionary

This document describes the structure and meaning of the processed datasets used in the Hospital Management Decision Support System.

## 1. admissions.csv
- `admission_id`: Unique identifier for the hospital admission (String).
- `patient_id`: Foreign key linking to patient demographics (String).
- `bed_id`: Foreign key linking to the bed registry (String).
- `assigned_doctor_id`: Foreign key linking to the doctor on shift (String).
- `department`: Hospital department (ICU, General Ward, Emergency Room, HDU) (String).
- `admission_date`: Timestamp of patient admission (Datetime).
- `discharge_date`: Timestamp of patient discharge or "Active Patient" (Datetime/String).
- `waiting_time_mins`: Total time in minutes from arrival to bed assignment (Integer).
- `severity_score`: Patient acuity score from 1 to 10 (Integer).
- `length_of_stay_days`: Total days spent in the hospital (Float).
- `under_staffed_alert`: Boolean flag indicating if the ward was understaffed during admission (Boolean).

## 2. beds.csv
- `bed_id`: Unique identifier for the bed (String).
- `ward_name`: The ward/department the bed belongs to (String).
- `bed_type`: Type of bed (Standard, ICU-Bed, HDU-Bed, ER-Stretcher) (String).
- `is_occupied`: 1 if occupied, 0 if available (Integer).

## 3. waiting_times.csv
- `admission_id`: Unique identifier for the admission (String).
- `department`: Department where the wait occurred (String).
- `waiting_time_mins`: Total time in minutes from arrival to bed assignment (Integer).
- `admission_date`: Timestamp of the admission (Datetime).

## 4. doctor_workload.csv
- `doctor_id`: Unique identifier for the doctor (String).
- `doctor_name`: Name of the doctor (String).
- `specialty`: Medical specialty (Critical Care, Pediatrics, Internal Medicine, Emergency Medicine) (String).
- `assigned_shift`: Shift timing (Day Shift or Night Shift) (String).
- `max_capacity`: Maximum safe patient load for the doctor (Integer).
- `active_patients`: Current number of patients assigned (Integer).
- `workload_pct`: Percentage of max capacity currently utilized (Float).

## 5. disease_trends.csv
- `month_year`: Month and Year of admissions (YYYY-MM) (String).
- `total_admissions`: Total number of patients admitted that month (Integer).
- `high_risk_patients`: Count of patients with >= 2 chronic conditions (Integer).
- `avg_chronic_conditions`: Average number of chronic conditions per patient (Float).
