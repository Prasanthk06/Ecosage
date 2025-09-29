#!/bin/bash

echo "🚀 Starting EcoSage Backend Server..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "Please edit .env with your database configuration"
    read -p "Press enter to continue..."
fi

# Initialize database
echo "🗄️  Initializing database..."
python init_db.py

# Start the server
echo "🌟 Starting Flask server..."
python app.py