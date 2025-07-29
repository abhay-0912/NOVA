@echo off
REM NOVA Setup Script for Windows
REM This script sets up the development environment for NOVA

echo 🧠 Setting up NOVA development environment...

REM Create virtual environment
echo 📦 Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install Python dependencies
echo 📚 Installing Python dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo 📁 Creating directories...
if not exist "data\chroma_db" mkdir data\chroma_db
if not exist "logs" mkdir logs
if not exist "cache" mkdir cache
if not exist "backups" mkdir backups
if not exist "config" mkdir config

REM Initialize configuration
echo ⚙️ Creating initial configuration...
echo nova: > config\config.yaml
echo   name: "NOVA" >> config\config.yaml
echo   personality: "assistant" >> config\config.yaml
echo   debug_mode: false >> config\config.yaml
echo. >> config\config.yaml
echo capabilities: >> config\config.yaml
echo   voice_enabled: true >> config\config.yaml
echo   vision_enabled: true >> config\config.yaml
echo   learning_enabled: true >> config\config.yaml
echo. >> config\config.yaml
echo security: >> config\config.yaml
echo   level: "high" >> config\config.yaml
echo   real_time_monitoring: true >> config\config.yaml
echo   auto_threat_response: true >> config\config.yaml
echo   data_encryption: true >> config\config.yaml
echo. >> config\config.yaml
echo database: >> config\config.yaml
echo   memory_db: "data/nova_memory.db" >> config\config.yaml
echo   vector_db: "data/chroma_db" >> config\config.yaml
echo. >> config\config.yaml
echo api: >> config\config.yaml
echo   host: "localhost" >> config\config.yaml
echo   port: 8000 >> config\config.yaml
echo   cors_origins: ["*"] >> config\config.yaml

echo.
echo ✅ NOVA setup completed!
echo.
echo 🚀 To start NOVA:
echo    python main.py
echo.
echo 📚 For help:
echo    python main.py --help
echo.
echo 🌐 Web interface will be available at:
echo    http://localhost:8000
echo.
pause
