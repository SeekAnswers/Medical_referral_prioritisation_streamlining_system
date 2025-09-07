@echo off
setlocal enabledelayedexpansion

REM Enhanced start.bat for Medical Referral System
echo ================================================================
echo 🏥 Medical Referral Priority System - Windows Launcher
echo ================================================================
echo.

REM Check for different Bash environments
set BASH_FOUND=0

REM Check Git Bash
where bash >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Git Bash found
    set BASH_FOUND=1
    bash deploy.sh
    goto :end
)

REM Check WSL
where wsl >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ WSL found
    set BASH_FOUND=1
    wsl bash deploy.sh
    goto :end
)

REM Check PowerShell (for alternative approach)
where powershell >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠️  No Bash environment found
    echo.
    echo Available options:
    echo   1. Install Git for Windows (includes Git Bash)
    echo   2. Enable WSL (Windows Subsystem for Linux)
    echo   3. Use Docker Desktop directly
    echo.
    choice /c 123 /m "Choose option (1-3): "
    if !errorlevel!==1 (
        start https://git-scm.com/download/win
        echo Opening Git for Windows download page...
    )
    if !errorlevel!==2 (
        start ms-windows-store://pdp/?ProductId=9n6svws3rx71
        echo Opening WSL in Microsoft Store...
    )
    if !errorlevel!==3 (
        echo Running Docker Compose directly...
        docker-compose up --build -d
    )
)

:end
echo.
echo Deployment process completed.
pause