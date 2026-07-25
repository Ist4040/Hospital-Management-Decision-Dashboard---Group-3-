import pandas as pd
import os
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Check both root and DATA folder for the excel file
raw_file_root = BASE_DIR / "Hospital_DSS_Real_World_Enterprise_Dataset_5K (1).xlsx"
raw_file_data = BASE_DIR / "DATA" / "Hospital_DSS_Real_World_Enterprise_Dataset_5K (1).xlsx"

if raw_file_root.exists():
    RAW_DATA_PATH = raw_file_root
elif raw_file_data.exists():
    RAW_DATA_PATH = raw_file_data
else:
    raise FileNotFoundError("Excel file not found! Please upload 'Hospital_DSS_Real_World_Enterprise_Dataset_5K (1).xlsx' to the main folder or the DATA folder.")

def load_and_process_data():
    print("🔄 Loading raw data from Excel...")
    
    # Read all sheets
    patient_demo = pd.read_excel(RAW_DATA_PATH, sheet_name="Patient Demographics")
    bed_registry = pd.read_excel(RAW_DATA_PATH, sheet_name="Bed Registry")
    doctor_roster = pd.read_excel(RAW_DATA_PATH, sheet_name="Doctor Shift Roster")
    admissions = pd.read_excel(RAW_DATA_PATH, sheet_name="Admission Records")

    # --- 1. Clean Admissions & Calculate Length of Stay ---
    admissions['admission_date'] = pd.to_datetime(admissions['admission_date'])
    admissions['discharge_date'] = pd.to_datetime(admissions['discharge_date'], errors='coerce')
    
    admissions['length_of_stay_days'] = (admissions['discharge_date'] - admissions['admission_date']).dt.days
    admissions['length_of_stay_days'] = admissions['length_of_stay_days'].fillna(0).round(1)

    # --- 2. Clean Doctor Workload & Calculate Percentage ---
    doctor_workload = doctor_roster.copy()
    doctor_workload['workload_pct'] = (doctor_workload['active_patients'] / doctor_workload['max_capacity'] * 100).round(1)

    # --- 3. Clean Patient Demographics & Calculate Risk Segment ---
    patient_demo = patient_demo.copy()
    patient_demo['risk_segment'] = patient_demo['chronic_conditions_count'].apply(lambda x: 'High' if x >= 2 else 'Low')

    # --- 4. Create Waiting Times & Disease Trends ---
    waiting_times = admissions[['admission_id', 'department', 'waiting_time_mins', 'admission_date']].copy()
    
    merged = admissions.merge(patient_demo[['patient_id', 'risk_segment', 'chronic_conditions_count']], on='patient_id', how='left')
    merged['month_year'] = merged['admission_date'].dt.to_period('M').astype(str)
    
    disease_trends = merged.groupby('month_year').agg(
        total_admissions=('admission_id', 'count'),
        high_risk_patients=('risk_segment', lambda x: (x == 'High').sum()),
        avg_chronic_conditions=('chronic_conditions_count', 'mean')
    ).reset_index()

    # --- 5. Save to CSV ---
    DATA_DIR.mkdir(exist_ok=True)
    
    admissions.to_csv(DATA_DIR / "admissions.csv", index=False)
    bed_registry.to_csv(DATA_DIR / "beds.csv", index=False)
    doctor_workload.to_csv(DATA_DIR / "doctor_workload.csv", index=False)
    patient_demo.to_csv(DATA_DIR / "patient_demographics.csv", index=False)
    waiting_times.to_csv(DATA_DIR / "waiting_times.csv", index=False)
    disease_trends.to_csv(DATA_DIR / "disease_trends.csv", index=False)
    
    print("✅ Data processing complete! CSVs saved to /data folder.")
    print(f"📊 Admissions: {len(admissions)} rows")
    print(f"🛏️ Beds: {len(bed_registry)} rows")
    print(f"👨‍⚕️ Doctors: {len(doctor_workload)} rows")
    print(f"👥 Patients: {len(patient_demo)} rows")

if __name__ == "__main__":
    load_and_process_data()
