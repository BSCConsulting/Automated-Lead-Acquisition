#!/bin/bash

# ==============================================================================
# 1-Click Desktop Startup Launcher for AP & TS Lead Intelligence Platform
# ==============================================================================

PROJECT_DIR="/Users/johnyforever/.gemini/antigravity/scratch/cosmetics_distribution_platform"
cd "$PROJECT_DIR" || exit 1

echo "=============================================================================="
echo "💄 AP & TS Cosmetics B2B Lead Intelligence Platform Launcher"
echo "=============================================================================="

# Check if mini_app_server.py is already running on port 3000
if lsof -i :3000 > /dev/null 2>&1; then
    echo "✅ Background Lead Engine is already running on http://localhost:3000"
else
    echo "🚀 Starting Background Lead Engine on http://localhost:3000..."
    nohup .venv/bin/python mini_app_server.py > /dev/null 2>&1 &
    sleep 2
fi

echo "🌐 Opening Platform in Google Chrome..."
open -a "Google Chrome" "http://localhost:3000" || open "http://localhost:3000"

echo "=============================================================================="
echo "🎉 Platform launched successfully! You may close this window."
echo "=============================================================================="
