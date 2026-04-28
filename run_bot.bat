@echo off
title Telegram AI IT Automation Agent
echo ====================================================
echo    Starting Telegram AI IT Automation Agent...
echo ====================================================
cd /d "%~dp0"

echo [1/2] Checking dependencies...
pip install -r requirements.txt > nul 2>&1

echo [2/2] Launching the bot...
python -m src.main

echo.
echo Bot stopped or encountered an error.
pause
