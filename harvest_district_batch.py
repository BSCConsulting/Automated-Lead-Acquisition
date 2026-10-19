import os
import re
import sys
import json
import time
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from dotenv import load_dotenv

import harvester
from mini_app_server import derive_district

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PhaseHarvester")

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
LEADS_DB_PATH = "leads_master_local.json"

CATEGORIES = [
    ("Beauty Parlour", "Commercial"),
    ("Hair Salon", "Commercial"),
    ("Cosmetics Shop", "Commercial"),
    ("Beauty Products Wholesaler", "Commercial"),
    ("Pharmacy", "Commercial"),
    ("Womens Degree College", "Institutional")
]

PHASE_DEFINITIONS = {
    "1": {
        "name": "Phase 1: Khammam & Bhadradri Kothagudem District Cluster",
        "filter": lambda d, s: any(k in d.lower() for k in ["khammam", "bhadradri", "kothagudem"])
    },
    "2": {
        "name": "Phase 2: Warangal, Hanamkonda & Karimnagar Hubs",
        "filter": lambda d, s: any(k in d.lower() for k in ["warangal", "hanamkonda", "karimnagar"])
    },
    "3": {
        "name": "Phase 3: Hyderabad, Rangareddy & Medchal Metro Core",
        "filter": lambda d, s: any(k in d.lower() for k in ["hyderabad", "rangareddy", "medchal"])
    },
    "4": {
        "name": "Phase 4: NTR (Vijayawada) & Guntur Commercial Belt",
        "filter": lambda d, s: any(k in d.lower() for k in ["ntr", "vijayawada", "guntur"])
    },
    "5": {
        "name": "Phase 5: Visakhapatnam & Kakinada / Coastal Hubs",
        "filter": lambda d, s: any(k in d.lower() for k in ["visakhapatnam", "kakinada", "godavari", "eluru"])
    },
    "6": {
        "name": "Phase 6: Rayalaseema & All Remaining Mandals",
        "filter": lambda d, s: not any(k in d.lower() for k in [
            "khammam", "bhadradri", "kothagudem",
            "warangal", "hanamkonda", "karimnagar",
            "hyderabad", "rangareddy", "medchal",
            "ntr", "vijayawada", "guntur",
            "visakhapatnam", "kakinada", "godavari", "eluru"
        ])
    }
}

def normalize_phone(raw_phone):
    if not raw_phone:
        return None, False
    digits = re.sub(r"\D", "", str(raw_phone))
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]
    
    if len(digits) == 10 and digits[0] in "6789":
        return f"+91{digits}", True
    elif len(digits) >= 10:
        return f"+91{digits}", True
    return None, False

def harvest_location_places(loc_key, loc_info, district_name):
    town = loc_info.get("town", loc_key)
    pincode = loc_info.get("pincode", "")
    state = loc_info.get("state", "Telangana")

    if not GOOGLE_MAPS_API_KEY:
        return []

    found_places = {}

    def search_category(cat_tuple):
        cat_name, seg = cat_tuple
        query_str = f"{cat_name} in {town} {pincode} {state} India"
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {"query": query_str, "key": GOOGLE_MAPS_API_KEY}
        cat_results = []
        try:
            resp = requests.get(url, params=params, timeout=8)
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                for place in results:
                    pid = place.get("place_id")
                    if pid:
                        place["target_segment"] = seg
                        place["target_category"] = cat_name
                        cat_results.append((pid, place))
        except Exception as e:
            logger.debug(f"Search error for {query_str}: {e}")
        return cat_results

    with ThreadPoolExecutor(max_workers=6) as executor:
        for cat_res in executor.map(search_category, CATEGORIES):
            for pid, place in cat_res:
                if pid not in found_places:
                    found_places[pid] = place

    # Step 2: Fetch details concurrently
    def fetch_details(item):
        pid, place = item
        det_url = "https://maps.googleapis.com/maps/api/place/details/json"
        fields = "name,formatted_address,formatted_phone_number,international_phone_number,geometry,rating,user_ratings_total,url,website"
        d_params = {"place_id": pid, "fields": fields, "key": GOOGLE_MAPS_API_KEY}
        
        bname = place.get("name", "").strip()
        addr = place.get("formatted_address", "").strip()
        geom = place.get("geometry", {}).get("location", {})
        lat = geom.get("lat")
        lon = geom.get("lng")
        phone = None
        map_url = None
        website = None
        rating = place.get("rating")
        reviews = place.get("user_ratings_total", 0)

        try:
            d_resp = requests.get(det_url, params=d_params, timeout=5)
            if d_resp.status_code == 200:
                d_data = d_resp.json().get("result", {})
                phone = d_data.get("international_phone_number") or d_data.get("formatted_phone_number")
                map_url = d_data.get("url")
                website = d_data.get("website")
                if d_data.get("formatted_address"):
                    addr = d_data.get("formatted_address")
                if d_data.get("rating"):
                    rating = d_data.get("rating")
                if d_data.get("user_ratings_total"):
                    reviews = d_data.get("user_ratings_total")
        except Exception as e:
            logger.debug(f"Details error for {pid}: {e}")

        norm_p, is_valid = normalize_phone(phone)
        if not map_url and pid:
            map_url = f"https://www.google.com/maps/place/?q=place_id:{pid}"

        dedup_hash = f"{pid}_{norm_p}"

        return {
            "lead_id": f"real_{pid[:12]}",
            "place_id": pid,
            "business_name": bname,
            "segment": place.get("target_segment", "Commercial"),
            "category": place.get("target_category", "Beauty & Personal Care"),
            "state": state,
            "district": district_name,
            "town": town,
            "mandal": town,
            "pincode": pincode,
            "address_raw": addr,
            "primary_phone": norm_p,
            "raw_phone": phone,
            "phone_is_valid": is_valid,
            "rating": rating,
            "user_ratings_total": reviews,
            "lat": lat,
            "lon": lon,
            "website": website,
            "google_maps_url": map_url,
            "map_link": map_url,
            "acquisition_source": "google_places_verified_live",
            "lead_status": "New",
            "dedup_hash": dedup_hash
        }

    enriched = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        enriched = list(executor.map(fetch_details, found_places.items()))

    return enriched

def run_phase(phase_id, max_locations=None):
    phase_info = PHASE_DEFINITIONS.get(str(phase_id))
    if not phase_info:
        logger.error(f"Unknown phase: {phase_id}")
        return

    print(f"\n=======================================================")
    print(f"Starting {phase_info['name']}")
    print(f"=======================================================\n")

    # Load existing master database
    existing_pids = set()
    master_records = []
    if os.path.exists(LEADS_DB_PATH):
        with open(LEADS_DB_PATH, "r", encoding="utf-8") as f:
            master_records = json.load(f)
        for r in master_records:
            if r.get("place_id"):
                existing_pids.add(r["place_id"])
    print(f"Current Master DB: {len(master_records)} verified leads ({len(existing_pids)} unique Place IDs).")

    # Filter locations
    target_locations = []
    all_db = harvester.TOWN_PINCODE_DB
    for k, v in all_db.items():
        t = v.get("town", "")
        p = v.get("pincode", "")
        s = v.get("state", "Telangana")
        dist = derive_district(t, p, s)
        if phase_info["filter"](dist, s):
            target_locations.append((k, v, dist))

    if max_locations:
        target_locations = target_locations[:max_locations]

    print(f"Identified {len(target_locations)} locations for this phase.\n")

    new_leads_collected = 0
    start_time = time.time()

    for idx, (loc_key, loc_info, dist) in enumerate(target_locations, 1):
        town = loc_info.get("town", loc_key)
        pin = loc_info.get("pincode", "")
        print(f"[{idx}/{len(target_locations)}] Harvesting {town} (PIN: {pin}, Dist: {dist})...")

        places = harvest_location_places(loc_key, loc_info, dist)
        added_for_loc = 0
        for p in places:
            if p["place_id"] not in existing_pids:
                existing_pids.add(p["place_id"])
                master_records.append(p)
                added_for_loc += 1
                new_leads_collected += 1

        print(f" -> Found {len(places)} places ({added_for_loc} new unique leads added). Total Master Leads: {len(master_records)}")

        # Save checkpoint every 5 locations
        if idx % 5 == 0 or idx == len(target_locations):
            with open(LEADS_DB_PATH, "w", encoding="utf-8") as f:
                json.dump(master_records, f, indent=2)
            print(f"    [Checkpoint Saved] Database updated with {len(master_records)} records.")

    elapsed = round(time.time() - start_time, 2)
    print(f"\n=======================================================")
    print(f"Phase {phase_id} Complete!")
    print(f"Time Taken: {elapsed}s")
    print(f"New Genuine Leads Added: {new_leads_collected}")
    print(f"Total Master Leads Now: {len(master_records)}")
    print(f"=======================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=str, default="1", help="Phase number (1-6)")
    parser.add_argument("--max_locations", type=int, default=None, help="Limit number of locations for testing")
    args = parser.parse_args()
    run_phase(args.phase, args.max_locations)
