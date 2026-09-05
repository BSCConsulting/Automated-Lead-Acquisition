import unittest
import json
import os
import sys
import pandas as pd

# Ensure local workspace is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from harvester import (
    normalize_phone_number, generate_dedup_hash, detect_state_from_pincode, resolve_location_info,
    get_supabase_client as get_harvester_supabase,
    fetch_tradeindia_b2b_leads, fetch_sulekha_leads, fetch_asklaila_leads, fetch_social_media_serp_leads
)
from analytics_engine import calculate_lead_conversion_metrics, calculate_lead_score_and_potential, extract_lat_lon_from_record, enrich_leads_with_analytics

class TestCosmeticsPlatform(unittest.TestCase):

    # -------------------------------------------------------------------------
    # 1. Tests for harvester.py (Phone Normalization, Hashing & State Detection)
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
        self.assertEqual(detect_state_from_pincode("Khammam"), "Telangana")
        self.assertEqual(detect_state_from_pincode("Vijayawada"), "Andhra Pradesh")

    def test_location_resolution_by_town_name(self):
        info = resolve_location_info("Khammam")
        self.assertEqual(info["pincode"], "507001")
        self.assertEqual(info["state"], "Telangana")
        self.assertEqual(info["town"], "Khammam")

    def test_location_resolution_by_pincode(self):
        info = resolve_location_info("507203")
        self.assertEqual(info["pincode"], "507203")
        self.assertEqual(info["state"], "Telangana")
        self.assertEqual(info["town"], "Madhira")

    def test_supabase_client_placeholder_skipping(self):
        os.environ["SUPABASE_URL"] = "https://your-supabase-project-id.supabase.co"
        os.environ["SUPABASE_KEY"] = "your-supabase-key"
        client = get_harvester_supabase()
        self.assertIsNone(client)

    # -------------------------------------------------------------------------
    # 2. Tests for analytics_engine.py (Lead Scoring, Grading & Map Extraction)
    # -------------------------------------------------------------------------
    def test_lead_scoring_and_order_potential(self):
        sample_row = pd.Series({
            "business_name": "Lakme Salon Khammam",
            "segment": "Commercial",
            "primary_phone": "+919257788143",
            "phone_is_valid": True,
            "website": "https://salons.lakmesalon.in/",
            "google_maps_url": "https://www.google.com/maps/search/?api=1&query=17.24758,80.16815"
        })
        score, grade, potential = calculate_lead_score_and_potential(sample_row)
        self.assertEqual(score, 100)
        self.assertEqual(grade, "A+")
        self.assertEqual(potential, 45000.0)

    def test_lat_lon_extraction(self):
        sample_row = pd.Series({
            "google_maps_url": "https://www.google.com/maps/search/?api=1&query=17.24758,80.16815"
        })
        lat, lon = extract_lat_lon_from_record(sample_row)
        self.assertEqual(lat, 17.24758)
        self.assertEqual(lon, 80.16815)

    def test_analytics_conversion_funnel(self):
        sample_df = pd.DataFrame([
            {"lead_id": "1", "business_name": "Glow Salon", "segment": "Commercial", "state": "Telangana", "phone_is_valid": True, "lead_status": "Converted"},
            {"lead_id": "2", "business_name": "Womens Hostel", "segment": "Institutional", "state": "Andhra Pradesh", "phone_is_valid": False, "lead_status": "New"}
        ])
        metrics = calculate_lead_conversion_metrics(sample_df)
        self.assertEqual(metrics["total_leads"], 2)
        self.assertEqual(metrics["conversion_rate_pct"], 50.0)
        self.assertTrue(metrics["total_pipeline_value_inr"] > 0)

    # -------------------------------------------------------------------------
    # 3. Tests for Multi-Source Scrapers (TradeIndia, Sulekha, AskLaila, Social)
    # -------------------------------------------------------------------------
    def test_tradeindia_scraper_returns_list(self):
        res = fetch_tradeindia_b2b_leads("Cosmetics Wholesaler", "507001", "Commercial", "Telangana")
        self.assertIsInstance(res, list)

    def test_sulekha_scraper_returns_list(self):
        res = fetch_sulekha_leads("Beauty Parlour", "507002", "Commercial", "Telangana")
        self.assertIsInstance(res, list)

    def test_asklaila_scraper_returns_list(self):
        res = fetch_asklaila_leads("Kirana General Store", "507203", "Commercial", "Telangana")
        self.assertIsInstance(res, list)

    def test_social_media_serp_scraper_returns_list(self):
        res = fetch_social_media_serp_leads("Unisex Salon", "500001", "Commercial", "Telangana")
        self.assertIsInstance(res, list)

if __name__ == "__main__":
    unittest.main()
