@echo off
title StickyTasks
cd /d "%~dp0"

REM --- try the Python launcher first, then plain python ---
py --version >nul 2>nul
if %errorlevel%==0 (
    py "%~dp0server.py" 8777
    goto :end
)

python --version >nul 2>nul
if %errorlevel%==0 (
    python "%~dp0server.py" 8777
    goto :end
)

echo.
echo   Python was not found on your computer.
echo   Floating Tasks needs Python to save your tasks to a real file.
echo.
echo   1. Install it from https://www.python.org/downloads/
echo      (on the first screen, tick "Add python.exe to PATH")
echo   2. Then double-click "Start Tasks" again.
echo.
pause

:end
