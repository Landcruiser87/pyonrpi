#!/usr/bin/env bash

# set -e
# This command is crucial. It causes the script to exit immediately
# if any command fails, preventing subsequent commands from running.
set -e

# 1. Get the absolute directory where this script is located.
# This makes the script location-agnostic and immune to CWD problems.
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

# 2. Define absolute paths to the venv Python and the script to run.
PROJECT_DIR="$HOME/gitrepos/pyonrpi"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
PYTHON_SCRIPT="$PROJECT_DIR/scripts/main.py"

# 3. Add a check to ensure the venv executable exists.
if [ ! -x "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment Python not found at $VENV_PYTHON"
    exit 1
fi

# 4. Execute the Python script using the robust "Direct Call" method.
echo "Starting Python script at $(date)..."
"$VENV_PYTHON" "$PYTHON_SCRIPT"
echo "Python script finished at $(date)."