#!/bin/bash
# Setup script for LibraryDesk on macOS/Linux

set -e

echo "Setting up LibraryDesk..."

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env from example..."
    cp .env.example .env
    echo "Please edit .env with your Oracle credentials."
fi

echo "Setup complete. Run 'source venv/bin/activate && python app.py' to start."
