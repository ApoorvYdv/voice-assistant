#!/bin/bash

# Navigate to the backend directory
cd "$(dirname "$0")/../backend" || exit 1

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  pip install uv; uv venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install requirements using pip3 or pip
uv sync
