import sys
import os
import argparse
import unittest
import json
import subprocess

def main():
    parser = argparse.ArgumentParser(
        description="💄 Cosmetics B2B/B2C Multi-Agent Platform Unified CLI Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--phase", 
        type=str, 
        choices=["catalog", "harvest", "dashboard", "webhook", "social", "test"],
        default="dashboard",
        help="Select platform module phase to execute."
    )
    
    # Arguments for harvester phase
    parser.add_argument("--pincodes", type=str, default="500001, 520001", help="Comma-separated Indian PIN codes for harvesting.")
    parser.add_argument("--segments", type=str, default="Commercial,Institutional", help="Comma-separated business segments.")

    # Arguments for social agent phase
    parser.add_argument("--posts", type=int, default=5, help="Number of social posts to generate (70%% D2C / 30%% B2B split).")

    # Arguments for webhook server
    parser.add_argument("--port", type=int, default=8000, help="Port to run FastAPI sales webhook server.")

    args = parser.parse_args()

    # Determine Python Executable
    venv_python = os.path.join(os.path.dirname(__file__), ".venv", "bin", "python")
    python_bin = venv_python if os.path.exists(venv_python) else sys.executable

    print(f"\n🚀 Launching Cosmetics Platform Phase: [{args.phase.upper()}] using {python_bin}\n" + "="*70)

    if args.phase == "catalog":
        from catalog_ingest import run_catalog_ingestion
        print("Running CatalogGenius Vision Ingestion...")
        results = run_catalog_ingestion()
        print(f"Extraction Complete! Generated {len(results)} item records.")

    elif args.phase == "harvest":
        from harvester import run_harvester
        pin_list = [p.strip() for p in args.pincodes.split(",") if p.strip()]
        seg_list = [s.strip() for s in args.segments.split(",") if s.strip()]
        print(f"Running Lead Harvester for PIN Codes: {pin_list} | Segments: {seg_list}...")
        summary = run_harvester(pin_list, seg_list)
        print(json.dumps(summary, indent=2))

    elif args.phase == "dashboard":
        streamlit_bin = os.path.join(os.path.dirname(__file__), ".venv", "bin", "streamlit")
        if not os.path.exists(streamlit_bin):
            streamlit_bin = "streamlit"
        print("Starting Streamlit Data Acquisition Dashboard...")
        subprocess.run([streamlit_bin, "run", "app.py"])

    elif args.phase == "webhook":
        uvicorn_bin = os.path.join(os.path.dirname(__file__), ".venv", "bin", "uvicorn")
        if not os.path.exists(uvicorn_bin):
            uvicorn_bin = "uvicorn"
        print(f"Starting FastAPI Sales Conversion Webhook Server on port {args.port}...")
        subprocess.run([uvicorn_bin, "sales_webhook:app", "--host", "0.0.0.0", "--port", str(args.port), "--reload"])

    elif args.phase == "social":
        from social_agent import run_social_campaign_pipeline
        print(f"Running Social Media Agent for {args.posts} posts (70% D2C / 30% B2B split)...")
        posts = run_social_campaign_pipeline(total_posts=args.posts)
        print(json.dumps(posts, ensure_ascii=False, indent=2))

    elif args.phase == "test":
        print("Running Automated Test Suite (test_platform.py)...")
        subprocess.run([python_bin, "-m", "unittest", "test_platform.py"])

if __name__ == "__main__":
    main()
