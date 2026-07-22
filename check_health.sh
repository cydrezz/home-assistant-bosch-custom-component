#!/bin/bash
set -e

echo "========================================"
echo "   BOSCH COMPONENT HEALTH CHECK"
echo "========================================"

echo -e "\n[1/3] 🔍 Static Code Analysis (Ruff)..."
# Check only the custom component directory, ignore some common strict rules if needed
# We use || true so the script doesn't exit immediately if linting finds issues (we want to see them)
ruff check custom_components/bosch || true

echo -e "\n[2/3] 🧪 Running Unit Tests..."
# Run the existing test script
./unittests/run.sh

echo -e "\n[3/3] 📜 Checking Home Assistant Logs (Errors/Warnings)..."
LOG_FILE="config/home-assistant.log"
if [ -f "$LOG_FILE" ]; then
    echo "Last 5 Errors:"
    grep -i "ERROR" "$LOG_FILE" | tail -n 5 || echo "No errors found."
    
    echo -e "\nLast 5 Warnings:"
    grep -i "WARNING" "$LOG_FILE" | tail -n 5 || echo "No warnings found."
else
    echo "Log file not found at $LOG_FILE"
fi

echo -e "\n========================================"
echo "   ✅ Health Check Complete"
echo "========================================"
