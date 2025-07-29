@echo off
REM NOVA Start Script for Windows

echo 🚀 Starting NOVA...

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment not found. Run scripts\install.bat first
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check configuration
if not exist "config\config.yaml" (
    echo ⚙️ Configuration not found. Creating default config...
    if not exist "config" mkdir config
    echo nova: > config\config.yaml
    echo   name: "NOVA" >> config\config.yaml
    echo   personality: "assistant" >> config\config.yaml
    echo   debug_mode: false >> config\config.yaml
)

REM Pre-flight checks
echo 🔍 Running pre-flight checks...
python -c "import fastapi, uvicorn, pydantic" >nul 2>&1
if errorlevel 1 (
    echo ❌ Missing required dependencies. Run scripts\install.bat
    exit /b 1
)

echo ✅ Dependencies check passed

REM Create directories
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "cache" mkdir cache

REM Set environment
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Parse arguments
set MODE=cli
if "%1"=="web" set MODE=web
if "%1"=="api" set MODE=api
if "%1"=="daemon" set MODE=daemon

echo 🎯 Starting NOVA in %MODE% mode...

if "%MODE%"=="web" (
    echo 🌐 Starting web interface at http://localhost:8000
    python main.py --mode=web
) else if "%MODE%"=="api" (
    echo 🔌 Starting API server at http://localhost:8000
    uvicorn interfaces.api:app --host 0.0.0.0 --port 8000 --reload
) else if "%MODE%"=="daemon" (
    echo 👻 Starting NOVA as background service...
    start /b python main.py --mode=daemon > logs\nova.log 2>&1
    echo ✅ NOVA daemon started. Check logs\nova.log for output
) else (
    echo 💻 Starting NOVA CLI interface...
    python main.py
)
