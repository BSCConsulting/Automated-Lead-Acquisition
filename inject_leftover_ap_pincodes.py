import re
from scan_leftover_ap_pincodes import LEFTOVER_AP_PINCODES

with open("harvester.py", "r", encoding="utf-8") as f:
    content = f.read()

new_entries = []
added_keys = set()

for dist, pins in LEFTOVER_AP_PINCODES.items():
    new_entries.append(f"    # {dist.upper()} (LEFTOVER POSTAL PIN CODES & SUB-OFFICES)")
    for item in pins:
        pincode = item["pincode"]
        area = item["area"]
        key = f"pin_{pincode}_{re.sub(r'[^a-z0-9]', '', area.lower())[:15]}"
        if key in added_keys:
            key = key + "_dup"
        added_keys.add(key)
        
        entry_str = f'    "{key}": {{"town": "{area}", "state": "Andhra Pradesh", "pincode": "{pincode}", "pincodes": ["{pincode}"]}},'
        new_entries.append(entry_str)

formatted_code = "\n".join(new_entries)

# Insert right before def resolve_location_info in harvester.py
target_marker = 'def resolve_location_info(input_str: str) -> Dict[str, Any]:'
if target_marker in content:
    old_end = '    # --- END OF LOCATION DATABASE ---'
    if old_end in content:
        updated_content = content.replace(old_end, formatted_code + "\n\n    # --- END OF LOCATION DATABASE ---")
    else:
        # Fallback insert before def resolve_location_info
        updated_content = content.replace(target_marker, formatted_code + "\n\n" + target_marker)
        
    with open("harvester.py", "w", encoding="utf-8") as f:
        f.write(updated_content)
    print(f"Successfully injected {len(added_keys)} leftover AP postal PIN code definitions into harvester.py!")
else:
    print("Error: Target marker not found in harvester.py")
