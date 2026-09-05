import json
import shutil
import pandas as pd
from analytics_engine import export_leads_to_excel

# Load all records from leads_master_local.json
with open("leads_master_local.json", "r", encoding="utf-8") as f:
    records = json.load(f)

print(f"Total Verified Master Leads in JSON DB: {len(records)}")

df = pd.DataFrame(records)
excel_bytes = export_leads_to_excel(df)

output_filename = "ap_ts_master_lead_directory.xlsx"
with open(output_filename, "wb") as f:
    f.write(excel_bytes)

print(f"Successfully exported local Excel workbook: {output_filename}")

artifact_path = "/Users/johnyforever/.gemini/antigravity/brain/b74d5343-41bb-4784-b987-cb8c01d9d2ee/ap_ts_master_lead_directory.xlsx"
shutil.copyfile(output_filename, artifact_path)
print(f"Successfully copied to artifact directory: {artifact_path}")
