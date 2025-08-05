@echo off
echo Starting Sales Performance Leaderboard System - Version 3.0
echo ========================================
echo.

:: Check Python environment
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found, please install Python first
    pause
    exit /b 1
)

:: Check Streamlit
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    pip install streamlit pandas numpy plotly openpyxl
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Starting system...
echo The system will open automatically in your browser
echo If not opened automatically, please visit: http://localhost:8501
echo.
echo Press Ctrl+C to stop the system
echo ========================================

:: Start Streamlit application
streamlit run main.py --server.headless false

pause 