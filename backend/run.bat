@echo off
echo 🚀 Starting EcoSage Backend Server...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo ⚙️  Creating .env file...
    copy .env.example .env
    echo Please edit .env with your database configuration
    pause
)

REM Initialize database
echo 🗄️  Initializing database...
python init_db.py

REM Start the server
echo 🌟 Starting Flask server...
python app.py