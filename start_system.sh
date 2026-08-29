#!/bin/bash
# DAPPTRADE Quick Start Script
# This script starts the entire DAPPTRADE system with all required services

set -e  # Exit on error

echo "================================"
echo "DAPPTRADE System Startup"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 16+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js found: $(node -v)${NC}"

# Check Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found. Please install Python 3.9+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python found: $(python --version)${NC}"

# Check if hardhat is installed
if ! npx hardhat --version &> /dev/null; then
    echo -e "${RED}❌ Hardhat not found. Please run: npm install${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Hardhat found: $(npx hardhat --version)${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Please create it first.${NC}"
    echo "See END_TO_END_INTEGRATION_GUIDE.md for setup instructions."
    exit 1
fi
echo -e "${GREEN}✅ .env file found${NC}"

echo ""
echo "================================"
echo "Starting Services..."
echo "================================"
echo ""

# Start Hardhat node in background
echo "1️⃣  Starting Hardhat blockchain node..."
npx hardhat node > hardhat.log 2>&1 &
HARDHAT_PID=$!
echo -e "${GREEN}✅ Hardhat started (PID: $HARDHAT_PID)${NC}"

# Wait for hardhat to start
sleep 3

# Deploy contracts
echo ""
echo "2️⃣  Deploying smart contracts..."
npx hardhat run scripts/deploy.js --network localhost > deploy.log 2>&1
echo -e "${GREEN}✅ Contracts deployed${NC}"

# Run integration tests
echo ""
echo "3️⃣  Running integration tests..."
if command -v python &> /dev/null; then
    python scripts/integration_test.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Integration tests passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Some integration tests failed. Check the logs.${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping integration tests (Python not available)${NC}"
fi

echo ""
echo "================================"
echo "✅ System Ready!"
echo "================================"
echo ""
echo "📊 Next steps:"
echo "  1. Open another terminal and run: streamlit run app.py"
echo "  2. Open http://localhost:8501 in your browser"
echo "  3. Create an account and start trading!"
echo ""
echo "📝 Service Information:"
echo "  - Blockchain Node: http://127.0.0.1:8545"
echo "  - Hardhat PID: $HARDHAT_PID"
echo "  - Logs: hardhat.log, deploy.log"
echo ""
echo "⚠️  To stop the blockchain, run: kill $HARDHAT_PID"
echo ""
