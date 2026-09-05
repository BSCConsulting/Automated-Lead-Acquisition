import re
from generate_missing_ts_towns import TELANGANA_MISSING_TOWNS_BY_DISTRICT

with open("harvester.py", "r", encoding="utf-8") as f:
    content = f.read()

# Generate Python code for missing entries
new_entries = []
added_keys = set()

for dist, towns in TELANGANA_MISSING_TOWNS_BY_DISTRICT.items():
    new_entries.append(f"    # {dist.upper()} (ADDITIONAL MANDALS & TOWNS)")
    for t in towns:
        raw_name = t["town"]
        pincode = t["pincode"]
        # Generate clean key
        key = re.sub(r'[^a-z0-9]', '', raw_name.lower())
        if key in added_keys:
            continue
        added_keys.add(key)
        
        # Clean display town name
        entry_str = f'    "{key}": {{"town": "{raw_name}", "state": "Telangana", "pincode": "{pincode}", "pincodes": ["{pincode}"]}},'
        new_entries.append(entry_str)

formatted_code = "\n".join(new_entries)

# Insert before ANDHRA PRADESH STATE section in TOWN_PINCODE_DB
ap_marker = '    # --- ANDHRA PRADESH STATE'
if ap_marker in content:
    updated_content = content.replace(ap_marker, formatted_code + "\n\n" + ap_marker)
    with open("harvester.py", "w", encoding="utf-8") as f:
        f.write(updated_content)
    print(f"Successfully injected {len(added_keys)} new Telangana town definitions into harvester.py!")
else:
    print("Error: Could not find Andhra Pradesh marker in harvester.py")
