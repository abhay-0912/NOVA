#!/bin/bash

# NOVA Installation Script
# This script installs dependencies and sets up NOVA for deployment

echo "🧠 Installing NOVA dependencies..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d" " -f2 | cut -d"." -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv .venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/chroma_db
mkdir -p logs
mkdir -p cache
mkdir -p backups
mkdir -p config

# Set permissions
echo "🔐 Setting permissions..."
chmod +x scripts/*.sh
chmod +x scripts/*.bat

# Initialize configuration
echo "⚙️ Creating initial configuration..."
if [ ! -f config/config.yaml ]; then
    cat > config/config.yaml << EOF
nova:
  name: "NOVA"
  personality: "assistant"
  debug_mode: false
  
capabilities:
  voice_enabled: true
  vision_enabled: true
  security_enabled: true
  
security:
  real_time_monitoring: true
  auto_threat_response: true
  data_encryption: true
  
interfaces:
  api_host: "localhost"
  api_port: 8000
  cli_enabled: true
  web_enabled: true
EOF
fi

# Create environment file
if [ ! -f .env ]; then
    cat > .env << EOF
# NOVA Environment Configuration
NOVA_ENV=development
NOVA_LOG_LEVEL=INFO
NOVA_DATA_DIR=./data
NOVA_CACHE_DIR=./cache

# API Configuration
API_HOST=localhost
API_PORT=8000

# Security Configuration
SECURITY_MONITORING=true
SECURITY_AUTO_RESPONSE=true

# Optional: API Keys (set these for full functionality)
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here
EOF
fi

echo "✅ NOVA installation completed!"
echo "📖 Next steps:"
echo "   1. Configure API keys in .env file (optional)"
echo "   2. Run: ./scripts/start.sh"
echo "   3. Access web interface at http://localhost:8000"
echo "   4. Or use CLI: python main.py"
