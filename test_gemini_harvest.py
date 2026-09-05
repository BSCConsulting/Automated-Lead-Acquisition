import os
import json
import re
from dotenv import load_dotenv
load_dotenv()
from google import genai

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

prompt = """
Generate a comprehensive list of 20 real major beauty parlours, unisex salons, cosmetics shops, and pharmacies in Warangal, Telangana, India.
Return strictly a JSON array of objects with keys: business_name, category, address_raw, raw_phone, lat, lon.
"""

resp = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
text = resp.text
text = re.sub(r"```json|```", "", text).strip()
data = json.loads(text)
print("Gemini generated records count:", len(data))
print(json.dumps(data[:3], indent=2))
