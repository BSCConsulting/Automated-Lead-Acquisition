import json
import os
import pandas as pd
from typing import Dict, Any, List
try:
    from harvester import load_leads_data
except ImportError:
    load_leads_data = None

def calculate_lead_conversion_metrics(df_leads: pd.DataFrame) -> Dict[str, Any]:
    """Calculates lead lifecycle conversion funnel metrics and regional breakdown."""
    if df_leads.empty:
        return {
            "total_leads": 0,
            "status_breakdown": {},
            "segment_breakdown": {},
            "state_breakdown": {},
            "conversion_rate_pct": 0.0,
            "projected_monthly_revenue_inr": 0.0
        }

    total_leads = len(df_leads)
    status_counts = df_leads["lead_status"].value_counts().to_dict() if "lead_status" in df_leads.columns else {}
    segment_counts = df_leads["segment"].value_counts().to_dict() if "segment" in df_leads.columns else {}
    state_counts = df_leads["state"].value_counts().to_dict() if "state" in df_leads.columns else {}

    converted_count = status_counts.get("Converted", 0) + status_counts.get("Qualified", 0)
    conversion_rate = (converted_count / total_leads * 100) if total_leads > 0 else 0.0

    # Revenue Projection Model (Avg B2B Order: ₹15,000 | Avg Commercial Order: ₹25,000)
    commercial_leads = segment_counts.get("Commercial", 0)
    institutional_leads = segment_counts.get("Institutional", 0)
    
    projected_revenue = (commercial_leads * 25000 * 0.15) + (institutional_leads * 50000 * 0.10)

    return {
        "total_leads": total_leads,
        "status_breakdown": status_counts,
        "segment_breakdown": segment_counts,
        "state_breakdown": state_counts,
        "conversion_rate_pct": round(conversion_rate, 2),
        "projected_monthly_revenue_inr": round(projected_revenue, 2)
    }

def update_lead_status(lead_id: str, new_status: str, local_file: str = "leads_master_local.json") -> bool:
    """Updates lead status in local storage or Supabase."""
    if os.path.exists(local_file):
        try:
            with open(local_file, "r") as f:
                records = json.load(f)
            updated = False
            for r in records:
                if r.get("lead_id") == lead_id or r.get("dedup_hash") == lead_id:
                    r["lead_status"] = new_status
                    updated = True
                    break
            if updated:
                with open(local_file, "w") as f:
                    json.dump(records, f, indent=2)
                return True
        except Exception:
            pass
    return False

def approve_social_post(post_index: int, local_file: str = "social_posts_pending.json") -> bool:
    """Approves a pending social media post for publication."""
    if os.path.exists(local_file):
        try:
            with open(local_file, "r") as f:
                posts = json.load(f)
            if 0 <= post_index < len(posts):
                posts[post_index]["status"] = "Approved"
                with open(local_file, "w", encoding="utf-8") as f:
                    json.dump(posts, f, ensure_ascii=False, indent=2)
                return True
        except Exception:
            pass
    return False
