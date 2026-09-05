import os
import sys
import time
import json
import html
import logging
import urllib.parse
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

import harvester

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TelegramLeadBot")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

class TelegramLeadBot:
    def __init__(self, db_path: str = "leads_master_local.json"):
        self.db_path = db_path
        self.db_mtime = 0
        self.leads = []
        self._load_leads()
        self.offset = 0

    def _load_leads(self):
        if os.path.exists(self.db_path):
            try:
                mtime = os.path.getmtime(self.db_path)
                if mtime > self.db_mtime:
                    with open(self.db_path, "r", encoding="utf-8") as f:
                        self.leads = json.load(f)
                    self.db_mtime = mtime
                    logger.info(f"Loaded {len(self.leads)} master leads into Telegram Bot Engine (mtime: {mtime}).")
            except Exception as e:
                logger.error(f"Error loading {self.db_path}: {e}")

    def format_lead_card(self, lead: Dict[str, Any]) -> str:
        self._load_leads()  # Check for dynamic hot-reload
        
        name = str(lead.get("business_name", "Salon / Store"))
        category = str(lead.get("category", "Cosmetics Lead"))
        phone = str(lead.get("primary_phone", "N/A"))
        state = str(lead.get("state", "AP/TS"))
        pincode = str(lead.get("pincode", "N/A"))

        # Resolve Mandal & District dynamically if missing
        mandal = lead.get("mandal")
        district = lead.get("district")
        if not mandal or mandal in ["N/A", "None", ""] or not district or district in ["N/A", "None", ""]:
            res = harvester.resolve_location_info(pincode)
            if res:
                mandal = res.get("town", lead.get("town", "N/A"))
                district = res.get("district", "N/A")
            else:
                mandal = lead.get("town", "N/A")
                district = "Telangana/AP"

        mandal = str(mandal or "N/A")
        district = str(district or "N/A")

        # HTML Escape strings to prevent Telegram parse_mode errors
        safe_name = html.escape(name)
        safe_category = html.escape(category)
        safe_mandal = html.escape(mandal)
        safe_district = html.escape(district)
        safe_state = html.escape(state)
        safe_pincode = html.escape(pincode)
        safe_phone = html.escape(phone)

        maps_link = lead.get("map_link") or f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(name)}+{urllib.parse.quote(mandal)}+{urllib.parse.quote(state)}"

        # Clean phone for WhatsApp URL
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        if len(clean_phone) == 10:
            clean_phone = "91" + clean_phone
        elif not clean_phone:
            clean_phone = "910000000000"
        
        encoded_name = urllib.parse.quote(name)
        encoded_mandal = urllib.parse.quote(mandal)
        wa_link = f"https://wa.me/{clean_phone}?text=Hello%20{encoded_name}%2C%20special%20wholesale%20cosmetics%20offer%20for%20your%20outlet%20in%20{encoded_mandal}%21"

        card = f"<b>🏪 {safe_name}</b>\n"
        card += f"🏷️ <i>{safe_category}</i>\n"
        card += f"📍 <b>Location:</b> {safe_mandal}, {safe_district} Dist, {safe_state} ({safe_pincode})\n"
        card += f"📞 <b>Phone:</b> {safe_phone}\n\n"
        card += f"💬 <a href='{wa_link}'><b>Open Direct WhatsApp Chat</b></a>\n"
        card += f"🗺️ <a href='{maps_link}'><b>Navigate via Google Maps</b></a>"
        return card

    def search_leads(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        self._load_leads()
        q = query.strip().lower()
        results = []
        for l in self.leads:
            text = f"{l.get('business_name','')} {l.get('district','')} {l.get('mandal','')} {l.get('pincode','')} {l.get('town','')} {l.get('state','')}".lower()
            if q in text:
                results.append(l)
                if len(results) >= limit:
                    break
        return results

    def send_telegram_message(self, chat_id: str, text: str) -> bool:
        if not TELEGRAM_BOT_TOKEN:
            logger.warning("No TELEGRAM_BOT_TOKEN configured.")
            return False
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code != 200:
                logger.error(f"Telegram API Error {resp.status_code}: {resp.text}")
                # Fallback send without HTML parse_mode if formatting fails
                payload.pop("parse_mode", None)
                resp = requests.post(url, json=payload, timeout=10)
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send Telegram message to {chat_id}: {e}")
            return False

    def handle_command(self, chat_id: str, text: str):
        text_strip = text.strip()
        cmd = text_strip.lower()

        if cmd in ["/start", "/help", "hi", "hello"]:
            welcome = (
                "👋 <b>Welcome to AP & TS Cosmetics Lead Intelligence Bot!</b> 💄\n\n"
                f"I am connected to your master database with <b>{len(self.leads):,} verified leads</b> across <b>1,527 locations</b> in Telangana (33 Districts) & Andhra Pradesh (26 Districts).\n\n"
                "🔍 <b>How to use:</b>\n"
                "Simply send me any <b>Town, Mandal, PIN Code, or District</b>!\n\n"
                "<b>Examples:</b>\n"
                "• <code>Khammam</code> or <code>507001</code>\n"
                "• <code>Nizamabad</code> or <code>503001</code>\n"
                "• <code>Vijayawada</code> or <code>520001</code>\n"
                "• <code>Visakhapatnam</code> or <code>530001</code>\n"
                "• <code>Tirupati</code> or <code>517501</code>\n\n"
                "I will immediately reply with lead cards featuring <b>1-click WhatsApp messaging</b> and <b>Google Maps doorstep navigation</b>!"
            )
            self.send_telegram_message(chat_id, welcome)

        elif cmd == "/stats":
            ts_count = sum(1 for l in self.leads if l.get("state") == "Telangana")
            ap_count = sum(1 for l in self.leads if l.get("state") == "Andhra Pradesh")
            stats_msg = (
                "📊 <b>Master Database Statistics:</b>\n\n"
                f"• <b>Total Verified Leads:</b> {len(self.leads):,}\n"
                f"• <b>Telangana Leads:</b> {ts_count:,} (33 Districts, 703 Locations)\n"
                f"• <b>Andhra Pradesh Leads:</b> {ap_count:,} (26 Districts, 824 Locations)\n"
                f"• <b>Combined Total Locations:</b> 1,527 PIN Code & Mandal Hubs"
            )
            self.send_telegram_message(chat_id, stats_msg)

        else:
            # Treat text as search query
            clean_query = text_strip.replace("/search", "").strip()
            if not clean_query:
                clean_query = text_strip

            safe_query = html.escape(clean_query)
            self.send_telegram_message(chat_id, f"🔍 Searching master database for: <b>'{safe_query}'</b>...")
            results = self.search_leads(clean_query, limit=5)

            if not results:
                self.send_telegram_message(
                    chat_id, 
                    f"❌ No verified leads found matching <b>'{safe_query}'</b>.\nTry searching another PIN code (e.g. <code>507001</code>) or town name (e.g. <code>Khammam</code>)."
                )
                return

            for idx, lead in enumerate(results, 1):
                card_text = f"<b>Result #{idx} of {len(results)}</b>\n\n" + self.format_lead_card(lead)
                self.send_telegram_message(chat_id, card_text)
                time.sleep(0.1)  # Slight rate-limiting pause

    def start_polling(self):
        if not TELEGRAM_BOT_TOKEN:
            logger.error("Cannot start polling: TELEGRAM_BOT_TOKEN is missing!")
            return

        logger.info("Starting Telegram Bot long-polling daemon listener...")
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"

        while True:
            try:
                params = {"offset": self.offset, "timeout": 20}
                resp = requests.get(url, params=params, timeout=25)
                if resp.status_code == 200:
                    updates = resp.json().get("result", [])
                    for update in updates:
                        self.offset = update["update_id"] + 1
                        msg = update.get("message") or update.get("edited_message")
                        if msg and "text" in msg:
                            chat_id = str(msg["chat"]["id"])
                            user_text = msg["text"]
                            user_name = msg.get("from", {}).get("first_name", "User")
                            logger.info(f"Received message from {user_name} ({chat_id}): '{user_text}'")
                            self.handle_command(chat_id, user_text)
                else:
                    logger.warning(f"getUpdates returned HTTP {resp.status_code}: {resp.text}")
                    time.sleep(3)
            except Exception as e:
                logger.error(f"Polling error: {e}")
                time.sleep(3)

if __name__ == "__main__":
    bot = TelegramLeadBot()
    bot.start_polling()
