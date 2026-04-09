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

# Detect if running in Docker and set venv directory
if [ -f "/.dockerenv" ]; then
    VENV_DIR="venv_docker"
else
    VENV_DIR="venv_local"
fi

echo "========================================="
echo "Running tests"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "Please run: ./scripts/venv.sh"
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Add src to PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

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
