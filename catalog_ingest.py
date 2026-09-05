import os
import glob
import json
import logging
import pandas as pd
from PIL import Image
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
logger = logging.getLogger("CatalogGenius")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
RAW_INPUT_DIR = os.getenv("RAW_INPUT_DIR", "raw_input")
OUTPUT_CSV_FILE = "catalog_output.csv"

EXTRACTION_SYSTEM_PROMPT = """
You are an expert OCR and retail vision intelligence assistant for a cosmetics wholesale distribution platform.
Analyze the provided supplier image containing cosmetics catalog listings, product packaging, price tags, or invoice overlays.

Perform OCR and entity extraction. You MUST distinguish between:
1. Printed Maximum Retail Price (MRP): The official printed retail price on the product packaging/sticker.
2. Overlaid Wholesale Cost: Hand-written, stamped, or overlaid cost price supplied by the wholesaler/distributor.

Extract the details into a strictly formatted JSON object with the following fields:
{
  "canonical_title": "Full descriptive name of the product",
  "brand": "Manufacturer or brand name",
  "category": "Cosmetic category (e.g., Skincare, Haircare, Makeup, Fragrance, Bath & Body)",
  "variant_size": "Size, net weight, or volume (e.g., 100ml, 50g, Pack of 3)",
  "mrp": 0.00,
  "wholesale_cost": 0.00,
  "b2b_trade_price": 0.00
}

Calculated b2b_trade_price: If not explicitly printed, calculate b2b_trade_price as wholesale_cost or wholesale_cost * 1.05 (5% distributor margin).
Return ONLY the raw valid JSON object without markdown fences or additional commentary.
"""

def get_supabase_client() -> Optional[Any]:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SECRET_KEY", "").strip() or os.getenv("SUPABASE_KEY", "").strip()
    if not url or not key or "your-supabase" in url or "your-project-id" in url:
        return None
    if create_client:
        try:
            return create_client(url, key)
        except Exception as e:
            logger.error(f"Supabase connection error: {e}")
    return None

def process_catalog_image(image_path: str) -> Dict[str, Any]:
    """
    Processes a single raw catalog image using Gemini API for OCR and pricing extraction.
    """
    logger.info(f"Processing image: {image_path}")
    image_name = os.path.basename(image_path)
    
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        logger.warning("GEMINI_API_KEY not found in environment. Generating simulated vision extraction.")
        return {
            "image_name": image_name,
            "canonical_title": f"Simulated Product ({os.path.splitext(image_name)[0].replace('_', ' ').title()})",
            "brand": "Matte Perfection",
            "category": "Skincare",
            "variant_size": "50ml",
            "mrp": 499.00,
            "wholesale_cost": 280.00,
            "b2b_trade_price": 294.00,
            "status": "Simulated (Missing Gemini API Key)"
        }

    try:
        pil_image = Image.open(image_path)
        
        # New Google GenAI SDK
        if genai:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[pil_image, EXTRACTION_SYSTEM_PROMPT],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            raw_json_str = response.text
        elif legacy_genai:
            legacy_genai.configure(api_key=GEMINI_API_KEY)
            model = legacy_genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([EXTRACTION_SYSTEM_PROMPT, pil_image])
            raw_json_str = response.text
        else:
            raise RuntimeError("No Google GenAI SDK installed.")

        # Clean JSON response formatting if required
        clean_json = raw_json_str.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        
        extracted_data = json.loads(clean_json.strip())
        extracted_data["image_name"] = image_name
        extracted_data["status"] = "Success"
        return extracted_data

    except Exception as e:
        logger.error(f"Error processing image {image_path}: {e}")
        return {
            "image_name": image_name,
            "canonical_title": f"Raw Catalog Item - {image_name}",
            "brand": "Generic",
            "category": "Cosmetics",
            "variant_size": "Standard",
            "mrp": 0.0,
            "wholesale_cost": 0.0,
            "b2b_trade_price": 0.0,
            "status": f"Error: {str(e)}"
        }

def run_catalog_ingestion(raw_folder: str = RAW_INPUT_DIR) -> List[Dict[str, Any]]:
    """
    Scans raw_input folder for images, extracts metadata, and exports to CSV & Supabase.
    """
    if not os.path.exists(raw_folder):
        os.makedirs(raw_folder, exist_ok=True)
        logger.info(f"Created raw input directory at: {raw_folder}")

    supported_extensions = ["*.jpg", "*.jpeg", "*.png", "*.webp"]
    image_paths = []
    for ext in supported_extensions:
        image_paths.extend(glob.glob(os.path.join(raw_folder, ext)))

    if not image_paths:
        logger.info(f"No raw supplier images found in '{raw_folder}'. Generating sample placeholder file.")
        sample_path = os.path.join(raw_folder, "sample_lipstick_catalog.jpg")
        img = Image.new('RGB', (400, 400), color=(220, 100, 120))
        img.save(sample_path)
        image_paths.append(sample_path)

    results = []
    for path in image_paths:
        extracted = process_catalog_image(path)
        results.append(extracted)

    # Save to CSV
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_CSV_FILE, index=False)
    logger.info(f"Catalog extraction exported to {OUTPUT_CSV_FILE}")

    # Upsert to Supabase catalog_items table if connected
    supabase = get_supabase_client()
    if supabase:
        try:
            records = []
            for r in results:
                records.append({
                    "image_name": r.get("image_name"),
                    "canonical_title": r.get("canonical_title"),
                    "brand": r.get("brand"),
                    "category": r.get("category"),
                    "variant_size": r.get("variant_size"),
                    "mrp": float(r.get("mrp", 0.0)),
                    "wholesale_cost": float(r.get("wholesale_cost", 0.0)),
                    "b2b_trade_price": float(r.get("b2b_trade_price", 0.0)),
                    "extracted_metadata": r
                })
            supabase.table("catalog_items").insert(records).execute()
            logger.info("Inserted extracted records to Supabase catalog_items table.")
        except Exception as e:
            logger.error(f"Supabase insertion failed: {e}")

    return results

if __name__ == "__main__":
    logger.info("Executing CatalogGenius Vision Ingestion...")
    res = run_catalog_ingestion()
    print(json.dumps(res, indent=2))
