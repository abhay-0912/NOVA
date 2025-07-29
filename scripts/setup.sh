#!/bin/bash

# NOVA Setup Script
# This script sets up the development environment for NOVA

echo "🧠 Setting up NOVA development environment..."

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
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

# Set up git hooks (optional)
echo "🔗 Setting up git hooks..."
if [ -d ".git" ]; then
    cp scripts/pre-commit .git/hooks/
    chmod +x .git/hooks/pre-commit
fi

# Initialize configuration
echo "⚙️ Creating initial configuration..."
cat > config/config.yaml << EOF
nova:
  name: "NOVA"
  personality: "assistant"
  debug_mode: false
  
capabilities:
  voice_enabled: true
  vision_enabled: true
  learning_enabled: true
  
security:
  level: "high"
  real_time_monitoring: true
  auto_threat_response: true
  data_encryption: true

database:
  memory_db: "data/nova_memory.db"
  vector_db: "data/chroma_db"
  
api:
  host: "localhost"
  port: 8000
  cors_origins: ["*"]
EOF

echo "✅ NOVA setup completed!"
echo ""
echo "🚀 To start NOVA:"
echo "   python main.py"
echo ""
echo "📚 For help:"
echo "   python main.py --help"
echo ""
echo "🌐 Web interface will be available at:"
echo "   http://localhost:8000"
