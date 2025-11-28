#!/bin/bash
# Helper script to run the data seeding

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to project root
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the seeding script with correct PYTHONPATH
PYTHONPATH="$SCRIPT_DIR" python scripts/seed_data.py "$@"
