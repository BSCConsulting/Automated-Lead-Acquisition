import unittest
import json
import os
import sys

# Ensure local workspace is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from harvester import normalize_phone_number, generate_dedup_hash, detect_state_from_pincode
from sales_webhook import classify_inbound_intent, format_outbound_message, WHOLESALE_CATALOG_TEMPLATES
from social_agent import generate_social_post, B2B_CAMPAIGN_TOPICS, D2C_CAMPAIGN_TOPICS
from catalog_ingest import process_catalog_image

class TestCosmeticsPlatform(unittest.TestCase):

    # -------------------------------------------------------------------------
    # 1. Tests for harvester.py (Phone Normalization & Deduplication)
    # -------------------------------------------------------------------------
    def test_phone_normalization_valid_10_digit(self):
        phone, is_valid = normalize_phone_number("9848012345")
        self.assertTrue(is_valid)
        self.assertEqual(phone, "+919848012345")

    def test_phone_normalization_with_spaces_and_hyphens(self):
        phone, is_valid = normalize_phone_number(" +91 94401-87654 ")
        self.assertTrue(is_valid)
        self.assertEqual(phone, "+919440187654")

    def test_phone_normalization_with_leading_zero(self):
        phone, is_valid = normalize_phone_number("08008123987")
        self.assertTrue(is_valid)
        self.assertEqual(phone, "+918008123987")

    def test_phone_normalization_invalid_number(self):
        phone, is_valid = normalize_phone_number("12345")
        self.assertFalse(is_valid)
        
    def test_dedup_hash_case_insensitive_and_whitespace_invariant(self):
        hash1 = generate_dedup_hash("Glam Beauty Salon", "+919848012345", "500001")
        hash2 = generate_dedup_hash("  glam beauty salon  ", "+919848012345", "500001")
        self.assertEqual(hash1, hash2)

    def test_state_detection_from_pincode(self):
        self.assertEqual(detect_state_from_pincode("500001"), "Telangana")
        self.assertEqual(detect_state_from_pincode("520001"), "Andhra Pradesh")

    # -------------------------------------------------------------------------
    # 2. Tests for sales_webhook.py (Intent Classification & Template Formatting)
    # -------------------------------------------------------------------------
    def test_inbound_intent_catalog_request(self):
        result = classify_inbound_intent("Can you send me the wholesale catalog rate list?")
        self.assertEqual(result["intent"], "Catalog Request")
        self.assertEqual(result["action"], "Send Catalog PDF")

    def test_inbound_intent_order_inquiry(self):
        result = classify_inbound_intent("I want to place a bulk order for lipsticks")
        self.assertEqual(result["intent"], "Order Inquiry")
        self.assertEqual(result["action"], "Escalate to Sales Agent")

    def test_inbound_intent_opt_out(self):
        result = classify_inbound_intent("Please stop sending messages")
        self.assertEqual(result["intent"], "Opt Out")

    def test_outbound_message_formatting_commercial(self):
        msg = format_outbound_message("Glow Salon", "Commercial", "Telangana")
        self.assertIn("Glow Salon", msg)
        self.assertIn("Telangana", msg)
        self.assertIn("Salon & Spa", msg)

    # -------------------------------------------------------------------------
    # 3. Tests for social_agent.py (Bilingual Content Generation)
    # -------------------------------------------------------------------------
    def test_social_agent_b2b_post_structure(self):
        post = generate_social_post("B2B", B2B_CAMPAIGN_TOPICS[0])
        self.assertEqual(post["campaign_type"], "B2B")
        self.assertIn("visual_asset_prompt", post)
        self.assertIn("copy_english", post)
        self.assertIn("copy_telugu", post)
        self.assertTrue(len(post["copy_english"]) > 10)
        self.assertTrue(len(post["copy_telugu"]) > 10)

    def test_social_agent_d2c_post_structure(self):
        post = generate_social_post("D2C", D2C_CAMPAIGN_TOPICS[0])
        self.assertEqual(post["campaign_type"], "D2C")
        self.assertIn("copy_english", post)
        self.assertIn("copy_telugu", post)

if __name__ == "__main__":
    unittest.main()
