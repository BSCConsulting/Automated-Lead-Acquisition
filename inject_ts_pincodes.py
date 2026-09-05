import re
import scan_leftover_ts_pincodes

leftover_db = scan_leftover_ts_pincodes.LEFTOVER_TS_PINCODES

lines_to_add = ["\n    # --- TELANGANA STATE (LEFTOVER POSTAL PIN CODES & SUB-OFFICES) ---"]

existing_keys = set()
with open("harvester.py", "r") as f:
    harvester_content = f.read()

# Simple regex to extract existing keys in TOWN_PINCODE_DB
for line in harvester_content.splitlines():
    m = re.match(r'^\s*"(pin_\d+_[a-z0-9_]+)":', line)
    if m:
        existing_keys.add(m.group(1))

for dist, items in leftover_db.items():
    dist_title = dist.upper()
    lines_to_add.append(f"\n    # {dist_title} (LEFTOVER POSTAL PIN CODES & SUB-OFFICES)")
    for item in items:
        pincode = item["pincode"]
        area = item["area"]
        # Sanitize area to form key
        sanitized = re.sub(r'[^a-z0-9]', '', area.lower())[:15]
        base_key = f"pin_{pincode}_{sanitized}"
        key = base_key
        counter = 1
        while key in existing_keys:
            counter += 1
            key = f"{base_key}_{counter}"
        existing_keys.add(key)
        
        entry = f'    "{key}": {{"town": "{area}", "state": "Telangana", "pincode": "{pincode}", "pincodes": ["{pincode}"]}},'
        lines_to_add.append(entry)

# Remove trailing comma on last item if needed
if lines_to_add[-1].endswith(','):
    lines_to_add[-1] = lines_to_add[-1][:-1]

formatted_injection = "\n".join(lines_to_add)

# Replace end of TOWN_PINCODE_DB in harvester.py
target_str = '    "pin_535441_palakondartccom": {"town": "Palakonda RTC Complex", "state": "Andhra Pradesh", "pincode": "535441", "pincodes": ["535441"]}\n}'

if target_str in harvester_content:
    new_target_str = '    "pin_535441_palakondartccom": {"town": "Palakonda RTC Complex", "state": "Andhra Pradesh", "pincode": "535441", "pincodes": ["535441"]},' + formatted_injection + '\n}'
    updated_content = harvester_content.replace(target_str, new_target_str)
    with open("harvester.py", "w") as f:
        f.write(updated_content)
    print("SUCCESS: Injected 166 leftover Telangana PIN codes into harvester.py!")
else:
    print("ERROR: Target string not found in harvester.py!")
