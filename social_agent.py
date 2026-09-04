import os
import json
import random
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

try:
    import google.generativeai as legacy_genai
except ImportError:
    legacy_genai = None

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SocialAgent")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

def get_supabase_client() -> Optional[Any]:
    if SUPABASE_URL and SUPABASE_KEY and create_client:
        try:
            return create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            logger.error(f"Supabase connection error: {e}")
    return None

B2B_CAMPAIGN_TOPICS = [
    "Wholesale price drops on matte lipstick bulk packs for salons in Hyderabad & Vijayawada",
    "Special distributor margin offer for regional beauty parlours and spa chains across AP & TS",
    "Direct manufacturer supply deals for pharmacy personal care sections in Guntur & Warangal"
]

D2C_CAMPAIGN_TOPICS = [
    "Festival glow makeup tips featuring waterproof foundation and vibrant lip shades",
    "Daily skincare routine for Indian tropical climate - hydra gels & sunscreens",
    "Organic herbal hair oil & nourishment serum launch promo"
]

SOCIAL_PROMPT_TEMPLATE = """
You are a creative social media manager for a premier cosmetics distribution brand operating in Andhra Pradesh and Telangana, India.

Generate social media content for a {campaign_type} campaign focused on: "{topic}".

Requirements:
1. Provide a detailed visual asset prompt for AI image generation (describing aesthetics, lighting, product arrangement, cultural elements).
2. Generate catchy, high-converting social media copy in English.
3. Translate and adapt the copy into natural, fluent Telugu (తెలుగు). Include appropriate regional hashtags (e.g. #TeluguBeauty, #APSalons, #TelanganaCosmetics, #HyderabadiBeauty).

Return ONLY valid JSON matching this schema:
{{
  "visual_asset_prompt": "Detailed description of the image prompt...",
  "copy_english": "English caption with emojis and hashtags...",
  "copy_telugu": "Telugu caption with emojis and hashtags..."
}}
"""

def generate_social_post(campaign_type: str, topic: str) -> Dict[str, Any]:
    """Generates bilingual social post copy and visual prompt using Gemini API."""
    logger.info(f"Generating {campaign_type} campaign content for topic: '{topic}'")

    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not configured. Generating simulated bilingual copy.")
        if campaign_type == "B2B":
            return {
                "campaign_type": campaign_type,
                "visual_asset_prompt": "Clean studio photography of wholesale cosmetic palette boxes stacked neatly, soft studio lighting, professional beauty salon background.",
                "copy_english": "💼 Salon Owners & Wholesalers in AP & TS! Get flat 35% margin on premium matte lipsticks this season. Doorstep delivery & GST invoicing! DM 'WHOLESALE' for price list. 💄✨ #APSalons #B2BCosmetics #HyderabadiBeauty",
                "copy_telugu": "💼 ఏపీ & తెలంగాణలోని బ్యూటీ సెలూన్ యజమానులకు శుభవార్త! టాప్ బ్రాండ్ మేకప్ కిట్స్‌పై 35% హోల్‌సేల్ మార్జిన్ పొందండి. హోమ్ డెలివరీ సదుపాయం కలదు! 💄✨ #TeluguBeauty #B2BCosmetics #BeautyParlourTelangana"
            }
        else:
            return {
                "campaign_type": campaign_type,
                "visual_asset_prompt": "Vibrant festive photoshoot of an South Indian woman with glowing skin, showcasing lip gloss and herbal skincare serums, warm sunlight.",
                "copy_english": "✨ Unlock your natural festive glow with our waterproof hydra-serum foundation! 🌿 Long-lasting, lightweight, and perfect for the sunny weather. Tap link in bio to shop! 🌸 #FestiveGlow #SkincareRoutine #IndianBeauty",
                "copy_telugu": "✨ మీ సహజమైన సౌందర్యాన్ని మెరిపించే వాటర్‌ప్రూఫ్ హైడ్రా సెరం! 🌿 మీ చర్మానికి పూర్తి రక్షణ మరియు రోజంతా మెరుపును అందిస్తుంది. ఇప్పుడే ఆర్డర్ చేయండి! 🌸 #TeluguSkincare #BeautyTipsTelugu #FestiveLook"
            }

    try:
        prompt_text = SOCIAL_PROMPT_TEMPLATE.format(campaign_type=campaign_type, topic=topic)
        
        if genai:
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt_text,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            raw_text = response.text
        elif legacy_genai:
            legacy_genai.configure(api_key=GEMINI_API_KEY)
            model = legacy_genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt_text)
            raw_text = response.text
        else:
            raise RuntimeError("No Google GenAI SDK installed.")

        clean_json = raw_text.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]

        parsed = json.loads(clean_json.strip())
        parsed["campaign_type"] = campaign_type
        return parsed

    except Exception as e:
        logger.error(f"Error generating content via Gemini: {e}")
        return {
            "campaign_type": campaign_type,
            "visual_asset_prompt": f"Product arrangement for {topic}",
            "copy_english": f"Special offer on {topic}! Contact us today for details.",
            "copy_telugu": f"{topic} పై ప్రత్యేకం ఆఫర్లు! మరిన్ని వివరాలకు సంప్రదించండి.",
        }

def run_social_campaign_pipeline(total_posts: int = 10) -> List[Dict[str, Any]]:
    """
    Main execution pipeline: Enforces a strict 70% D2C and 30% B2B split across generated posts.
    Saves generated content with status='Pending Approval' for human review.
    """
    b2b_count = int(total_posts * 0.30)
    d2c_count = total_posts - b2b_count

    logger.info(f"Initiating social media campaign pipeline: Total={total_posts} (70% D2C = {d2c_count}, 30% B2B = {b2b_count})")

    generated_posts = []

    # Generate 30% B2B Commercial Posts
    for i in range(b2b_count):
        topic = random.choice(B2B_CAMPAIGN_TOPICS)
        post = generate_social_post("B2B", topic)
        post["status"] = "Pending Approval"
        generated_posts.append(post)

    # Generate 70% D2C Consumer Posts
    for i in range(d2c_count):
        topic = random.choice(D2C_CAMPAIGN_TOPICS)
        post = generate_social_post("D2C", topic)
        post["status"] = "Pending Approval"
        generated_posts.append(post)

    # Save output to Supabase social_posts or local JSON file
    supabase = get_supabase_client()
    if supabase:
        try:
            records = []
            for p in generated_posts:
                records.append({
                    "campaign_type": p["campaign_type"],
                    "visual_asset_prompt": p["visual_asset_prompt"],
                    "copy_english": p["copy_english"],
                    "copy_telugu": p["copy_telugu"],
                    "status": p["status"]
                })
            res = supabase.table("social_posts").insert(records).execute()
            logger.info("Successfully inserted generated social posts to Supabase social_posts table.")
        except Exception as e:
            logger.error(f"Supabase insertion failed: {e}")
    else:
        local_file = "social_posts_pending.json"
        with open(local_file, "w", encoding="utf-8") as f:
            json.dump(generated_posts, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(generated_posts)} posts with 'Pending Approval' status to {local_file}")

    return generated_posts

if __name__ == "__main__":
    logger.info("Executing Social Media Automation Agent...")
    posts = run_social_campaign_pipeline(total_posts=5)
    print(json.dumps(posts, ensure_ascii=False, indent=2))
