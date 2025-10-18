@echo off
title Quick Deployment Package Creator
echo.
echo =============================================
echo    DEPLOYMENT PACKAGE CREATOR
echo =============================================
echo.

set "deploy_folder=karma_monitor_package"

echo Creating deployment package...

if exist "%deploy_folder%" rmdir /s /q "%deploy_folder%"
mkdir "%deploy_folder%"

echo Copying files...
copy "tiktok_webhook_monitor.py" "%deploy_folder%\"
copy "requirements.txt" "%deploy_folder%\"
copy "start_monitor.bat" "%deploy_folder%\"
copy "updater.py" "%deploy_folder%\"
copy "version.json" "%deploy_folder%\"
copy "setup_friend.bat" "%deploy_folder%\"
copy "DEPLOYMENT_GUIDE.md" "%deploy_folder%\"

echo.
echo =============================================
echo    PACKAGE READY!
echo =============================================
echo.
echo Your deployment package is in: %deploy_folder%\
echo.
echo What to send your friend:
echo  1. Zip the '%deploy_folder%' folder
echo  2. Send the zip file
echo  3. Tell them to:
echo     - Extract the zip
echo     - Run setup_friend.bat
echo     - Run start_monitor.bat
echo.
echo That's it! They'll have a working Karma Monitor!
echo.

pause