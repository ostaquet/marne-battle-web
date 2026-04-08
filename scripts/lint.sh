#!/bin/bash
# Run all linters on the project

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
echo "Running linters"
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

# Run flake8
echo -e "${YELLOW}[1/2] Running flake8...${NC}"
if flake8 src/ test/ --max-line-length=88 --extend-ignore=E203 --ignore=W293; then
    echo -e "${GREEN}✓ flake8 passed${NC}"
else
    echo -e "${RED}✗ flake8 failed${NC}"
    exit 1
fi
echo ""

# Run mypy
echo -e "${YELLOW}[2/2] Running mypy...${NC}"
if mypy src/ --strict; then
    echo -e "${GREEN}✓ mypy passed${NC}"
else
    echo -e "${RED}✗ mypy failed${NC}"
    exit 1
fi
echo ""

echo "========================================="
echo -e "${GREEN}All linters passed successfully!${NC}"
echo "========================================="
