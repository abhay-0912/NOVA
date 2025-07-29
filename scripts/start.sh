#!/bin/bash

# NOVA Start Script
# This script starts NOVA with appropriate configuration

echo "🚀 Starting NOVA..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run ./scripts/install.sh first"
    exit 1
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Check if configuration exists
if [ ! -f "config/config.yaml" ]; then
    echo "⚙️ Configuration not found. Creating default config..."
    mkdir -p config
    cat > config/config.yaml << EOF
nova:
  name: "NOVA"
  personality: "assistant"
  debug_mode: false
EOF
fi

# Pre-flight checks
echo "🔍 Running pre-flight checks..."

# Check Python dependencies
python -c "import fastapi, uvicorn, pydantic" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing required dependencies. Run ./scripts/install.sh"
    exit 1
fi

echo "✅ Dependencies check passed"

# Create necessary directories
mkdir -p data logs cache

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Parse command line arguments
MODE="cli"
if [ "$1" = "web" ]; then
    MODE="web"
elif [ "$1" = "api" ]; then
    MODE="api"
elif [ "$1" = "daemon" ]; then
    MODE="daemon"
fi

echo "🎯 Starting NOVA in $MODE mode..."

case $MODE in
    "web")
        echo "🌐 Starting web interface at http://localhost:8000"
        python main.py --mode=web
        ;;
    "api")
        echo "🔌 Starting API server at http://localhost:8000"
        uvicorn interfaces.api:app --host 0.0.0.0 --port 8000 --reload
        ;;
    "daemon")
        echo "👻 Starting NOVA as background daemon..."
        nohup python main.py --mode=daemon > logs/nova.log 2>&1 &
        echo "✅ NOVA daemon started. Check logs/nova.log for output"
        ;;
    *)
        echo "💻 Starting NOVA CLI interface..."
        python main.py
        ;;
esac
