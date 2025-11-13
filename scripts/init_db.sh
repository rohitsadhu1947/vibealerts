#!/bin/bash
# Initialize Neon database with schema

set -e  # Exit on error

echo "🗄️  Initializing Vibe Alerts Database..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please copy .env.example to .env and fill in your credentials"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL not set in .env"
    exit 1
fi

echo "📡 Connecting to database..."
echo "Host: $(echo $DATABASE_URL | sed 's/.*@//' | sed 's/:.*//')"
echo ""

# Run schema
echo "Creating tables..."
psql "$DATABASE_URL" -f src/database/schema.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database initialized successfully!"
    echo ""
    echo "Tables created:"
    psql "$DATABASE_URL" -c "\dt" 2>/dev/null || echo "  (Run: psql \$DATABASE_URL -c '\\dt' to see tables)"
else
    echo ""
    echo "❌ Database initialization failed"
    exit 1
fi

