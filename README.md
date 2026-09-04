# 💄 Cosmetics B2B/B2C Multi-Agent Distribution Platform

An end-to-end multi-agent B2B/B2C cosmetics distribution platform designed for Andhra Pradesh (AP) and Telangana (TS). The system integrates vision-based supplier catalog ingestion, automated lead harvesting with phone hygiene, a multi-tab Streamlit dashboard, a FastAPI WhatsApp/Voice sales conversion webhook, and a bilingual (Telugu/English) social media automation agent.

---

## 🏗️ Architecture & Modules

```
cosmetics_distribution_platform/
├── .env.example                     # Environment configuration template
├── requirements.txt                 # Python dependencies manifest
├── schema.sql                       # Complete PostgreSQL schema for Supabase
├── Dockerfile                       # Production container definition
├── docker-compose.yml               # Multi-container orchestration
├── main.py                          # Unified CLI Launcher across all phases
├── analytics_engine.py              # Funnel analytics, revenue modeling & post approval
├── test_platform.py                 # Automated unit test suite (12 tests)
├── catalog_ingest.py                # Phase 0: Vision OCR & Pricing Extraction Pipeline
├── harvester.py                     # Phase 1: Lead acquisition, regex phone hygiene, SHA-256 dedup
├── app.py                           # Multi-Tab Streamlit Dashboard & Admin Panel
├── sales_webhook.py                 # Phase 2: FastAPI WhatsApp & Voice Sales Conversion Webhook
└── social_agent.py                  # Phase 3: Bilingual (Telugu/English) Social Media Agent
```

---

## ⚡ Quick Start & Setup

### 1. Environment Setup
```bash
# Clone or navigate to the workspace
cd /Users/johnyforever/.gemini/antigravity/scratch/cosmetics_distribution_platform

# Create virtual environment and install dependencies
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your API credentials:
```bash
cp .env.example .env
```
Key configuration parameters:
- `SUPABASE_URL` & `SUPABASE_KEY` (PostgreSQL Database)
- `GEMINI_API_KEY` (OCR Vision & Telugu/English Copy Generation)
- `WHATSAPP_CLOUD_API_TOKEN` & `WHATSAPP_PHONE_ID` (Outbound Sales Webhook)

---

## 🎮 Unified CLI Launcher (`main.py`)

Run any module phase directly using `main.py`:

```bash
# Run unit tests
.venv/bin/python main.py --phase test

# Harvest leads for specific PIN codes & segments
.venv/bin/python main.py --phase harvest --pincodes 500001,520001 --segments Commercial,Institutional

# Run Gemini Vision catalog ingestion
.venv/bin/python main.py --phase catalog

# Generate social media posts (70% D2C / 30% B2B split)
.venv/bin/python main.py --phase social --posts 10

# Launch Streamlit Control Center
.venv/bin/python main.py --phase dashboard

# Start FastAPI Sales Webhook listener
.venv/bin/python main.py --phase webhook --port 8000
```

---

## 🐳 Docker Deployment

To launch both the Streamlit Dashboard (port `8501`) and FastAPI Webhook Server (port `8000`) using Docker:

```bash
docker-compose up --build
```

---

## 🧪 Automated Testing

Run the unit test suite to verify phone regex validation, SHA-256 deduplication hashing, intent routing, and bilingual copy generation:

```bash
.venv/bin/python -m unittest test_platform.py
```
