import os
import json
import logging
import urllib.parse
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

import harvester
import analytics_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MiniWebAppServer")

app = FastAPI(
    title="AP & TS Cosmetics B2B Lead Intelligence Mini Web App",
    description="Standalone Local Mini Web App with Spotlight Search, Kanban Board, Leaflet Maps, and 1-Click WhatsApp Dispatches.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LEADS_DB_PATH = "leads_master_local.json"
_cached_leads: List[Dict[str, Any]] = []
_cached_mtime: float = 0.0

def get_master_leads() -> List[Dict[str, Any]]:
    global _cached_leads, _cached_mtime
    if os.path.exists(LEADS_DB_PATH):
        try:
            mtime = os.path.getmtime(LEADS_DB_PATH)
            if mtime > _cached_mtime or not _cached_leads:
                with open(LEADS_DB_PATH, "r", encoding="utf-8") as f:
                    _cached_leads = json.load(f)
                _cached_mtime = mtime
                logger.info(f"Loaded {len(_cached_leads)} master leads into Mini Web App memory.")
        except Exception as e:
            logger.error(f"Error loading {LEADS_DB_PATH}: {e}")
    return _cached_leads

class LeadStatusUpdate(BaseModel):
    lead_id: str
    status: str

@app.get("/api/health")
def health_check():
    leads = get_master_leads()
    return {
        "status": "online",
        "service": "AP & TS Cosmetics Lead Intelligence Mini Web App Engine",
        "total_leads": len(leads),
        "total_locations": len(harvester.TOWN_PINCODE_DB)
    }

@app.get("/api/leads")
def get_leads(
    q: Optional[str] = Query(None, description="Search term across business name, pincode, town, mandal, district, state"),
    state: Optional[str] = Query(None, description="Filter by state (Telangana or Andhra Pradesh)"),
    district: Optional[str] = Query(None, description="Filter by district name"),
    segment: Optional[str] = Query(None, description="Filter by segment (Commercial or Institutional)"),
    status: Optional[str] = Query(None, description="Filter by status (New, Contacted, Sample Sent, Qualified, Wholesale Client)"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    leads = get_master_leads()
    filtered = leads

    if state and state.lower() != "all":
        st_lower = state.strip().lower()
        filtered = [l for l in filtered if l.get("state", "").lower() == st_lower]

    if district and district.lower() != "all":
        dist_lower = district.strip().lower()
        filtered = [l for l in filtered if dist_lower in l.get("district", "").lower() or dist_lower in l.get("town", "").lower()]

    if segment and segment.lower() != "all":
        seg_lower = segment.strip().lower()
        filtered = [l for l in filtered if l.get("segment", "").lower() == seg_lower]

    if status and status.lower() != "all":
        stat_lower = status.strip().lower()
        filtered = [l for l in filtered if l.get("lead_status", "New").lower() == stat_lower]

    if q:
        query_terms = q.strip().lower().split()
        def matches(lead):
            text = f"{lead.get('business_name','')} {lead.get('district','')} {lead.get('mandal','')} {lead.get('pincode','')} {lead.get('town','')} {lead.get('state','')} {lead.get('category','')}".lower()
            return all(term in text for term in query_terms)
        filtered = [l for l in filtered if matches(l)]

    total_matched = len(filtered)
    paged = filtered[offset : offset + limit]

    # Enrich lead records with WhatsApp URLs & Maps URLs
    for lead in paged:
        name = lead.get("business_name", "Salon / Store")
        mandal = lead.get("mandal") or lead.get("town") or "Location"
        state_val = lead.get("state") or "AP/TS"
        phone = str(lead.get("primary_phone") or "")
        
        clean_phone = "".join(filter(str.isdigit, phone))
        if len(clean_phone) == 10:
            clean_phone = "91" + clean_phone
        elif not clean_phone:
            clean_phone = "910000000000"
            
        encoded_name = urllib.parse.quote(name)
        encoded_mandal = urllib.parse.quote(mandal)
        lead["whatsapp_url"] = f"https://wa.me/{clean_phone}?text=Hello%20{encoded_name}%2C%20special%20wholesale%20cosmetics%20offer%20for%20your%20outlet%20in%20{encoded_mandal}%21"
        if not lead.get("map_link"):
            lead["map_link"] = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(name)}+{urllib.parse.quote(mandal)}+{urllib.parse.quote(state_val)}"

    return {
        "total": total_matched,
        "limit": limit,
        "offset": offset,
        "leads": paged
    }

@app.get("/api/stats")
def get_stats():
    leads = get_master_leads()
    ts_count = sum(1 for l in leads if l.get("state") == "Telangana")
    ap_count = sum(1 for l in leads if l.get("state") == "Andhra Pradesh")
    valid_phones = sum(1 for l in leads if l.get("phone_is_valid"))
    
    # Calculate pipeline value
    total_val = 0.0
    district_counts = {}
    for l in leads:
        bname = str(l.get("business_name", "")).lower()
        seg = str(l.get("segment", ""))
        dist = str(l.get("district") or l.get("town") or "Other")
        district_counts[dist] = district_counts.get(dist, 0) + 1
        
        if seg == "Institutional":
            total_val += 60000.0
        elif any(k in bname for k in ["salon", "spa", "parlour", "makeover"]):
            total_val += 45000.0
        elif any(k in bname for k in ["pharmacy", "medical", "medplus", "apollo"]):
            total_val += 30000.0
        else:
            total_val += 15000.0

    top_districts = dict(sorted(district_counts.items(), key=lambda x: x[1], reverse=True)[:10])

    return {
        "total_leads": len(leads),
        "telangana_leads": ts_count,
        "andhra_leads": ap_count,
        "valid_phone_leads": valid_phones,
        "phone_hygiene_pct": round((valid_phones / len(leads) * 100) if leads else 0, 1),
        "total_locations": len(harvester.TOWN_PINCODE_DB),
        "total_pipeline_value_inr": round(total_val, 2),
        "top_districts": top_districts
    }

@app.post("/api/leads/update-status")
def update_status(payload: LeadStatusUpdate):
    success = analytics_engine.update_lead_status(payload.lead_id, payload.status)
    if success:
        # Reload leads in memory
        get_master_leads()
        return {"status": "success", "lead_id": payload.lead_id, "new_status": payload.status}
    else:
        raise HTTPException(status_code=404, detail="Lead not found or update failed")

@app.get("/", response_class=HTMLResponse)
def serve_app():
    with open("mini_app_frontend.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
