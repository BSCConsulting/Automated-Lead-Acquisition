import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel, Field
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = Any

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SalesWebhook")

app = FastAPI(
    title="Cosmetics B2B Sales Conversion Agent API",
    description="FastAPI webhook listener for outbound WhatsApp/Voice dispatch and inbound intent classification.",
    version="1.0.0"
)

# Credentials
WHATSAPP_TOKEN = os.getenv("WHATSAPP_CLOUD_API_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

def get_supabase_client() -> Optional[Client]:
    if SUPABASE_URL and SUPABASE_KEY and create_client:
        try:
            return create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            logger.error(f"Supabase client initialization error: {e}")
    return None

# Pydantic Schemas
class OutboundTriggerRequest(BaseModel):
    batch_size: int = Field(default=10, ge=1, le=100)
    segments: Optional[List[str]] = None
    simulate_only: bool = False

class InboundMessagePayload(BaseModel):
    from_phone: str
    message_text: str
    lead_id: Optional[str] = None
    channel: str = Field(default="whatsapp")

# Segment-specific Wholesale Catalog Templates
WHOLESALE_CATALOG_TEMPLATES: Dict[str, Dict[str, str]] = {
    "Commercial": {
        "header": "🌟 Exclusive Wholesale Salon & Spa Cosmetics Deal 🌟",
        "body": "Hello {business_name},\n\nSpecial wholesale offers for commercial outlets in {state}! Get up to 40% margin on top skincare, hair care, and professional makeup kits.\n\n👉 View Catalog & Wholesale Rates: https://catalog.cosmeticsdist.in/salon-wholesale",
        "cta": "Reply 'CATALOG' for instant PDF price list."
    },
    "Institutional": {
        "header": "🏫 Institutional Bulk Supplies - Beauty & Personal Hygiene 🏫",
        "body": "Hello {business_name},\n\nWholesale bulk supply deals tailored for hostels & institutions in {state}. Direct manufacturer pricing on daily personal care, soap, shampoo, and sanitary kits.\n\n👉 View Institutional Rate Card: https://catalog.cosmeticsdist.in/institutional-bulk",
        "cta": "Reply 'BULK' for custom quote."
    },
    "Default": {
        "header": "💄 B2B Wholesale Cosmetics Distribution Offers 💄",
        "body": "Hello {business_name},\n\nDirect distribution rates on top cosmetic brands in {state}. High margins & doorstep delivery.\n\n👉 View B2B Offer Sheet: https://catalog.cosmeticsdist.in/b2b-offers",
        "cta": "Reply 'YES' to talk to sales agent."
    }
}

def format_outbound_message(business_name: str, segment: str, state: str) -> str:
    template = WHOLESALE_CATALOG_TEMPLATES.get(segment, WHOLESALE_CATALOG_TEMPLATES["Default"])
    msg = f"{template['header']}\n\n{template['body'].format(business_name=business_name, state=state)}\n\n{template['cta']}"
    return msg

def dispatch_whatsapp_message(to_phone: str, text_message: str) -> bool:
    """Dispatches message via WhatsApp Cloud API or logs payload in simulation mode."""
    if WHATSAPP_TOKEN and WHATSAPP_PHONE_ID:
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone.replace("+", ""),
            "type": "text",
            "text": {"body": text_message}
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code in [200, 201]:
                logger.info(f"WhatsApp message dispatched to {to_phone}")
                return True
            else:
                logger.error(f"WhatsApp API Error {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            logger.error(f"Exception during WhatsApp dispatch: {e}")
            return False
    else:
        logger.info(f"[SIMULATED DISPATCH] To: {to_phone} | Body:\n{text_message}")
        return True

def classify_inbound_intent(message_text: str) -> Dict[str, Any]:
    text_lower = message_text.lower()
    if any(k in text_lower for k in ["catalog", "price", "rate", "list", "pdf"]):
        return {
            "intent": "Catalog Request",
            "response": "Here is our latest wholesale catalog PDF: https://catalog.cosmeticsdist.in/download/latest.pdf",
            "action": "Send Catalog PDF"
        }
    elif any(k in text_lower for k in ["order", "buy", "discount", "margin", "bulk"]):
        return {
            "intent": "Order Inquiry",
            "response": "Thank you for your interest! A wholesale account manager will call you within 15 minutes to take your bulk order.",
            "action": "Escalate to Sales Agent"
        }
    elif any(k in text_lower for k in ["stop", "unsubscribe", "remove"]):
        return {
            "intent": "Opt Out",
            "response": "You have been unsubscribed from our wholesale updates.",
            "action": "Update Lead Status to Unsubscribed"
        }
    else:
        return {
            "intent": "General Inquiry",
            "response": "Thank you for contacting us! Reply 'CATALOG' for prices or 'ORDER' to speak with a representative.",
            "action": "Auto Reply"
        }

@app.get("/health")
def health_check():
    return {"status": "online", "service": "Cosmetics Sales Conversion Webhook Agent"}

@app.post("/outbound/trigger")
def trigger_outbound_campaign(request_data: OutboundTriggerRequest, background_tasks: BackgroundTasks):
    """
    Queries `leads_master` for records where `lead_status = 'New'`,
    formats personalized catalog offer, and initiates dispatch.
    """
    supabase = get_supabase_client()
    leads_to_process = []

    if supabase:
        try:
            query = supabase.table("leads_master").select("*").eq("lead_status", "New").eq("phone_is_valid", True)
            if request_data.segments:
                query = query.in_("segment", request_data.segments)
            response = query.limit(request_data.batch_size).execute()
            leads_to_process = response.data or []
        except Exception as e:
            logger.error(f"Error querying Supabase for new leads: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Fallback to local JSON DB
        local_file = "leads_master_local.json"
        if os.path.exists(local_file):
            with open(local_file, "r") as f:
                data = json.load(f)
                leads_to_process = [r for r in data if r.get("lead_status") == "New" and r.get("phone_is_valid")]
                leads_to_process = leads_to_process[:request_data.batch_size]

    if not leads_to_process:
        return {"status": "complete", "message": "No new valid leads found for dispatch.", "dispatched_count": 0}

    dispatched_list = []
    for lead in leads_to_process:
        phone = lead.get("primary_phone")
        name = lead.get("business_name", "Valued Partner")
        seg = lead.get("segment", "Commercial")
        state = lead.get("state", "AP/TS")
        
        msg_text = format_outbound_message(name, seg, state)
        
        if not request_data.simulate_only:
            success = dispatch_whatsapp_message(phone, msg_text)
            if success:
                # Update status in DB
                if supabase:
                    try:
                        supabase.table("leads_master").update({"lead_status": "Contacted"}).eq("lead_id", lead["lead_id"]).execute()
                    except Exception as e:
                        logger.error(f"Failed to update lead_status for {lead['lead_id']}: {e}")
                
                dispatched_list.append({"lead_id": lead.get("lead_id"), "phone": phone, "status": "Contacted"})
        else:
            dispatched_list.append({"lead_id": lead.get("lead_id"), "phone": phone, "status": "Simulated", "preview": msg_text})

    return {
        "status": "success",
        "total_queued": len(leads_to_process),
        "dispatched_count": len(dispatched_list),
        "dispatches": dispatched_list
    }

@app.post("/inbound/handle")
def handle_inbound_message(payload: InboundMessagePayload):
    """
    Receives incoming customer intent, classifies action, and returns automated response payload.
    """
    classification = classify_inbound_intent(payload.message_text)
    
    logger.info(f"Inbound message from {payload.from_phone} | Intent: {classification['intent']}")
    
    # Auto-dispatch response if credentials available
    if payload.from_phone:
        dispatch_whatsapp_message(payload.from_phone, classification["response"])

    return {
        "status": "processed",
        "from_phone": payload.from_phone,
        "classified_intent": classification["intent"],
        "action_taken": classification["action"],
        "auto_reply_sent": classification["response"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
