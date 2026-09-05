import re
from generate_missing_ap_towns import AP_MISSING_TOWNS_BY_DISTRICT

with open("harvester.py", "r", encoding="utf-8") as f:
    content = f.read()

new_entries = []
added_keys = set()

for dist, towns in AP_MISSING_TOWNS_BY_DISTRICT.items():
    new_entries.append(f"    # {dist.upper()} (ADDITIONAL MANDALS & TOWNS)")
    for t in towns:
        raw_name = t["town"]
        pincode = t.get("pincode", "520001")
        # Clean unique key
        key = re.sub(r'[^a-z0-9]', '', raw_name.lower())
        if key in added_keys:
            key = key + "_ap"
        added_keys.add(key)
        
        entry_str = f'    "{key}": {{"town": "{raw_name}", "state": "Andhra Pradesh", "pincode": "{pincode}", "pincodes": ["{pincode}"]}},'
        new_entries.append(entry_str)

formatted_code = "\n".join(new_entries)

# Target insertion point right before def resolve_location_info
target_marker = 'def resolve_location_info(input_str: str) -> Dict[str, Any]:'
if target_marker in content:
    # Insert formatted_code before def resolve_location_info with closing brace adjustment
    # We replace the line '    "yerragondapalem": {"town": "Yerragondapalem", "state": "Andhra Pradesh", "pincode": "523327", "pincodes": ["523327"]}'
    old_end = '"yerragondapalem": {"town": "Yerragondapalem", "state": "Andhra Pradesh", "pincode": "523327", "pincodes": ["523327"]}'
    new_end = old_end + ",\n\n" + formatted_code
    
    updated_content = content.replace(old_end, new_end)
    with open("harvester.py", "w", encoding="utf-8") as f:
        f.write(updated_content)
    print(f"Successfully injected {len(added_keys)} new Andhra Pradesh town definitions into harvester.py!")
else:
    print("Error: Target marker not found in harvester.py")
