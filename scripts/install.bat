@echo off
REM NOVA Installation Script for Windows

echo 🧠 Installing NOVA dependencies...

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+ first
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment
echo 📦 Creating Python virtual environment...
python -m venv .venv

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing Python dependencies...
pip install -r requirements.txt

REM Create directories
echo 📁 Creating directories...
if not exist "data\chroma_db" mkdir data\chroma_db
if not exist "logs" mkdir logs
if not exist "cache" mkdir cache
if not exist "backups" mkdir backups
if not exist "config" mkdir config

REM Create configuration
echo ⚙️ Creating initial configuration...
if not exist "config\config.yaml" (
    echo nova: > config\config.yaml
    echo   name: "NOVA" >> config\config.yaml
    echo   personality: "assistant" >> config\config.yaml
    echo   debug_mode: false >> config\config.yaml
    echo. >> config\config.yaml
    echo capabilities: >> config\config.yaml
    echo   voice_enabled: true >> config\config.yaml
    echo   vision_enabled: true >> config\config.yaml
    echo   security_enabled: true >> config\config.yaml
)

REM Create environment file
if not exist ".env" (
    echo # NOVA Environment Configuration > .env
    echo NOVA_ENV=development >> .env
    echo NOVA_LOG_LEVEL=INFO >> .env
    echo NOVA_DATA_DIR=./data >> .env
    echo NOVA_CACHE_DIR=./cache >> .env
    echo. >> .env
    echo # API Configuration >> .env
    echo API_HOST=localhost >> .env
    echo API_PORT=8000 >> .env
)

echo ✅ NOVA installation completed!
echo 📖 Next steps:
echo    1. Configure API keys in .env file (optional)
echo    2. Run: scripts\start.bat
echo    3. Access web interface at http://localhost:8000
echo    4. Or use CLI: python main.py

pause
