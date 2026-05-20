@echo off
title Telegram AI IT Automation Agent v2.0
echo ====================================================
echo    🤖 Telegram AI IT Automation Agent v2.0
echo ====================================================
cd /d "%~dp0"

echo [1/3] Checking Python version...
python --version

echo [2/3] Installing dependencies...
pip install -r requirements.txt > nul 2>&1

echo [3/3] Launching the bot...
echo.
python -m src.main

echo.
echo Bot stopped or encountered an error.
pause
