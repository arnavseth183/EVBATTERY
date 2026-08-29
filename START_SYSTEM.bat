@echo off
REM ==============================================
REM  EV Battery Passport System - Quick Start
REM  Windows Batch Script
REM ==============================================

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                                                                    ║
echo ║      🔋 EV BATTERY PASSPORT SYSTEM - AUTO STARTUP 🔋              ║
echo ║                                                                    ║
echo ║      Initializing: Data → ML Models → Blockchain → Dashboard      ║
echo ║                                                                    ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

REM Change to script directory
cd /d "%~dp0"

echo.
echo [Step 1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo    Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)
echo ✅ Python found

echo.
echo [Step 2/4] Generating battery data and training models...
echo           (This may take 1-2 minutes)
python scripts\battery_data_loader.py
if errorlevel 1 (
    echo ❌ Error generating battery data
    pause
    exit /b 1
)
echo ✅ Battery data generated

python ai_oracle\training\battery_health_trainer.py
if errorlevel 1 (
    echo ❌ Error training models
    pause
    exit /b 1
)
echo ✅ ML models trained

echo.
echo [Step 3/4] Starting Streamlit dashboard...
echo           (This may take 30 seconds to start)
echo           (Dashboard will open in your default browser)
streamlit run app.py --logger.level=error

echo.
echo [Step 4/4] Dashboard stopped. Cleanup...
echo ✅ System shutdown complete

pause
