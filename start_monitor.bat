@echo off
title Lacs TikTok Monitor
cd /d "%~dp0"
chcp 65001 >nul

echo.
echo  _       _    ___  ___   __  __  ___  _  _ ___ _____ ___  ___ 
echo ^| ^|     /_\  ^|_ _^|^|_ _^| ^|  \/  ^|^|   \^| \^| ^|_ _^|_   _^|   \^|   \
echo ^| ^|__  / _ \  ^| ^| ^| ^|  ^| ^|\/^| ^|^| ^|\ ^| .` ^|^| ^|  ^| ^| ^| ^|\ ^| ^|\ ^|
echo ^|____^|/_/ \_\^|___^|^|___^| ^|_^|  ^|_^|^|_^|_\_^|_\__^|^|___^| ^|_^| ^|_^|_^|_^|_^|_^|
echo ================================================================
echo.

REM Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Create a flag file to track if dependencies are installed
set DEPS_INSTALLED_FLAG=.deps_installed

REM Check if dependencies need to be installed
if not exist "%DEPS_INSTALLED_FLAG%" (
    echo [INFO] First run detected - installing dependencies...
    pip install -r requirements.txt --quiet --no-warn-script-location --force-reinstall
    if %errorlevel% equ 0 (
        echo [SUCCESS] Dependencies installed successfully
        echo Dependencies installed on %date% %time% > "%DEPS_INSTALLED_FLAG%"
    ) else (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    REM Quick check if packages are still available using our dependency checker
    python check_deps.py >nul 2>&1
    if %errorlevel% neq 0 (
        echo [INFO] Dependencies missing - reinstalling...
        pip install -r requirements.txt --quiet --no-warn-script-location --force-reinstall
        if %errorlevel% neq 0 (
            echo [ERROR] Failed to reinstall dependencies
            del "%DEPS_INSTALLED_FLAG%" >nul 2>&1
            pause
            exit /b 1
        )
        echo [SUCCESS] Dependencies reinstalled successfully
        echo Dependencies reinstalled on %date% %time% > "%DEPS_INSTALLED_FLAG%"
    )
)

REM Check for updates automatically
if exist updater.py (
    echo [INFO] Checking for updates...
    python updater.py --silent
    echo.
)

REM Run the monitor
echo [INFO] Starting Lacs TikTok Monitor...
echo ================================================================
echo.
python tiktok_webhook_monitor.py

REM If we get here, the monitor stopped
echo.
echo ================================================================
echo [INFO] Monitor stopped. Press any key to exit...
pause >nul