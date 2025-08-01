#!/bin/bash

# Best Buy Product Searcher Launcher
# This script launches the Python application

echo "🔍 Best Buy Product Searcher"
echo "============================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python version $python_version is too old"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

echo "✅ Python $python_version found"

# Run the launcher script
python3 run.py

# If the launcher script doesn't exist, run the main script directly
if [ $? -ne 0 ]; then
    echo "Trying to run main application directly..."
    python3 bestbuy_searcher.py
fi 