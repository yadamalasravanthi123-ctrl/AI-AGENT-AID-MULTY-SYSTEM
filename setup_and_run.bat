@echo off
setlocal EnableDelayedExpansion

echo.
echo ============================================================
echo   AI Legal Aid Multi-Agent System — Setup ^& Run
echo   Powered by IBM Granite (watsonx.ai)
echo ============================================================
echo.

:: ── Check Python ──────────────────────────────────────────────────────────
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [OK] Python %PYVER% found

:: ── Check Node ────────────────────────────────────────────────────────────
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js not found. Please install Node 18+ from https://nodejs.org
    pause
    exit /b 1
)
for /f "tokens=1" %%v in ('node --version') do set NODEVER=%%v
echo [OK] Node.js %NODEVER% found

:: ── Check npm ─────────────────────────────────────────────────────────────
where npm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] npm not found. Re-install Node.js from https://nodejs.org
    pause
    exit /b 1
)
for /f "tokens=1" %%v in ('npm --version') do set NPMVER=%%v
echo [OK] npm %NPMVER% found

echo.

:: ── Python virtual environment ────────────────────────────────────────────
if not exist "venv\Scripts\activate.bat" (
    echo [SETUP] Creating Python virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment already exists.
)

:: ── Activate venv ─────────────────────────────────────────────────────────
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated.

:: ── Install Python dependencies ───────────────────────────────────────────
echo [SETUP] Installing Python dependencies...
pip install -r requirements.txt --quiet
if %ERRORLEVEL% neq 0 (
    echo [ERROR] pip install failed. Check requirements.txt and your internet connection.
    pause
    exit /b 1
)
echo [OK] Python dependencies installed.

:: ── .env file ─────────────────────────────────────────────────────────────
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo.
    echo [ACTION REQUIRED] A .env file has been created from .env.example.
    echo            Please open .env and fill in your IBM watsonx.ai credentials:
    echo.
    echo            WATSONX_API_KEY      = your IBM Cloud API key
    echo            WATSONX_PROJECT_ID   = your watsonx.ai project ID
    echo.
    echo            Then re-run this script.
    echo.
    notepad .env
    pause
    exit /b 0
) else (
    echo [OK] .env file found.
)

:: ── Install Node dependencies ─────────────────────────────────────────────
if not exist "node_modules" (
    echo [SETUP] Installing Node.js dependencies...
    npm install --silent
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] npm install failed.
        pause
        exit /b 1
    )
    echo [OK] Node.js dependencies installed.
) else (
    echo [OK] node_modules already present.
)

:: ── Build React frontend ──────────────────────────────────────────────────
echo [SETUP] Building React frontend...
npm run build
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Frontend build failed. Check Vite / React errors above.
    pause
    exit /b 1
)
echo [OK] Frontend built into /dist

:: ── Start Flask server ────────────────────────────────────────────────────
echo.
echo ============================================================
echo   Starting Flask server on http://localhost:5000
echo   Press Ctrl+C to stop.
echo ============================================================
echo.
python app.py

pause
