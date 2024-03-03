#!/bin/bash

# Install all pip packages
# Check if pip is available
if command -v pip >/dev/null 2>&1; then
    pip install -r requirements.txt
# Check if pip3 is available
elif command -v pip3 >/dev/null 2>&1; then
    pip3 install -r requirements.txt
else
    echo "Error: Neither pip nor pip3 found. Please install pip or pip3."
    exit 1
fi

