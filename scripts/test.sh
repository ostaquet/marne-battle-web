#!/bin/bash
# Run all tests on the project

set -e  # Exit on first error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "========================================="
echo "Running tests"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run pytest with verbose output
echo -e "${YELLOW}Running pytest...${NC}"
if pytest test/ -v; then
    echo ""
    echo "========================================="
    echo -e "${GREEN}All tests passed successfully!${NC}"
    echo "========================================="
else
    echo ""
    echo "========================================="
    echo -e "${RED}Tests failed!${NC}"
    echo "========================================="
    exit 1
fi
