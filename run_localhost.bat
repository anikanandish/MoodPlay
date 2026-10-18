@echo off
title MoodPlay Web Server
echo ========================================================
echo  🎵 MoodPlay — Audiophile AI Music Companion (Localhost)
echo ========================================================
echo.
echo Starting local Ollama engine and MoodPlay server...
echo.

:: Ensure Ollama is running in background if not already
powershell -Command "if (-not (Get-Process *ollama* -ErrorAction SilentlyContinue)) { Start-Process 'ollama' -ArgumentList 'serve' -WindowStyle Hidden; Start-Sleep -Seconds 2 }"

echo.
echo ✨ Opening http://localhost:8000 in your browser...
start http://localhost:8000

echo.
echo ✨ Server running at: http://localhost:8000
echo ✨ Press Ctrl+C in this window to stop the server.
echo.

python app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Server exited with error code %ERRORLEVEL%.
    pause
)
