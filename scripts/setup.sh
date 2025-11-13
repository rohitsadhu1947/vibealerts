#!/bin/bash
# Quick setup script for Vibe Alerts

echo "🚀 Vibe Alerts Quick Setup"
echo "=========================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION found"

# Check if .env exists
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo ""
        echo "📝 Creating .env file from .env.example..."
        cp .env.example .env
        echo "✅ .env file created"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and fill in your credentials:"
        echo "   - DATABASE_URL (from Neon DB)"
        echo "   - TELEGRAM_BOT_TOKEN (from @BotFather)"
        echo "   - TELEGRAM_CHANNEL_ID (your channel username)"
        echo ""
        echo "Run this script again after editing .env"
        exit 0
    else
        echo "❌ .env.example not found"
        exit 1
    fi
fi

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate venv
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📚 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if Redis is running
echo ""
echo "🔍 Checking Redis..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "⚠️  Redis not running. Start it with:"
    echo "   macOS: brew services start redis"
    echo "   Linux: sudo systemctl start redis"
fi

# Initialize database
echo ""
echo "🗄️  Initializing database..."
if ./scripts/init_db.sh; then
    echo "✅ Database initialized"
else
    echo "⚠️  Database initialization failed (may already be initialized)"
fi

# Run tests
echo ""
echo "🧪 Running setup tests..."
python scripts/test_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✅ Setup complete! Ready to launch."
    echo "========================================="
    echo ""
    echo "Start Vibe Alerts:"
    echo "  python main.py"
    echo ""
else
    echo ""
    echo "⚠️  Some tests failed. Please fix the issues above."
    echo "See QUICKSTART.md for help."
fi
