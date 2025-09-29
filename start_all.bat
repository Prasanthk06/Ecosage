@echo off
echo 🚀 EcoSage Full-Stack Application Startup
echo ==========================================
echo.

echo 📊 Starting Model Server (Port 8080)...
start "Model Server" cmd /k "cd /d c:\Ecosage && python model_server.py"
timeout /t 3 /nobreak >nul

echo 🔧 Starting Backend API (Port 5000)...
start "Backend API" cmd /k "cd /d c:\Ecosage\backend && venv\Scripts\activate && python app_simple.py"
timeout /t 3 /nobreak >nul

echo 🌐 Starting Frontend (Port 3000)...
start "Frontend" cmd /k "cd /d c:\Ecosage && npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ✅ All services are starting up!
echo.
echo 🌐 Access your application at:
echo    Frontend:    http://localhost:3000
echo    Backend API: http://localhost:5000  
echo    Model Server: http://127.0.0.1:8080
echo.
echo 📱 Features Available:
echo    • Carbon Footprint Calculator
echo    • AI Waste Classification
echo    • Environmental Events Calendar
echo    • Real-time API Integration
echo.
echo ⏹️ To stop all services, close the command windows
echo.
pause