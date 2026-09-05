import json
import pandas as pd
from harvester import run_harvester, TOWN_PINCODE_DB
from analytics_engine import export_leads_to_excel

print(f"Starting statewide harvest for {len(TOWN_PINCODE_DB)} locations across Telangana & Andhra Pradesh...")

# Take all unique town keys
locations = list(TOWN_PINCODE_DB.keys())
segments = ["Commercial", "Institutional"]

# Run harvester
summary = run_harvester(locations, segments)

print(f"Harvest Complete!")
print(f"Total Processed: {summary.get('total_processed')}")
print(f"Newly Inserted: {summary.get('inserted_records')}")

# Load all records from leads_master_local.json
try:
    with open("leads_master_local.json", "r", encoding="utf-8") as f:
        records = json.load(f)
    print(f"Total Master Leads in Database: {len(records)}")
    
    df = pd.DataFrame(records)
    excel_bytes = export_leads_to_excel(df)
    
    output_filename = "ap_ts_master_lead_directory.xlsx"
    with open(output_filename, "wb") as f:
        f.write(excel_bytes)
        
    print(f"Successfully generated publication-grade Excel workbook: {output_filename}")
except Exception as e:
    print(f"Error exporting Excel: {e}")
