@echo off
title Karma Monitor Setup
echo.
echo =============================================
echo    KARMA MONITOR - FRIEND SETUP
echo =============================================
echo.
echo Installing Python dependencies...
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please install Python from https://python.org
    echo.
    pause
    exit /b 1
)

echo Python found! Installing requirements...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo =============================================
    echo    SETUP COMPLETE!
    echo =============================================
    echo.
    echo You can now run the monitor with:
    echo    start_monitor.bat
    echo.
    echo The monitor will:
    echo  - Check TikTok every 15 seconds
    echo  - Send Discord webhooks when live
    echo  - Show clean interface with uptime
    echo.
) else (
    echo.
    echo ERROR: Failed to install dependencies!
    echo Try running: pip install aiohttp requests
    echo.
)

pause