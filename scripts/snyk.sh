#!/bin/bash
# Run snyk dependency checks on the project

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
echo "Running Snyk on dependencies"
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

# Check if snyk is installed
if snyk --version; then
    echo -e "${GREEN}✓ snyk installed${NC}"
else
    echo -e "${RED}✗ snyk not installed${NC}"
    echo "Please install snyk following instructions on https://docs.snyk.io/developer-tools/snyk-cli/install-or-update-the-snyk-cli"
    exit 1
fi
echo ""

# Run snyk
echo -e "${YELLOW} Running snyk...${NC}"
if snyk test; then
    echo -e "${GREEN}✓ check passed${NC}"
else
    echo -e "${RED}✗ check failed${NC}"
    exit 1
fi
echo ""

echo "========================================="
echo -e "${GREEN}Dependencies checks passed successfully!${NC}"
echo "========================================="
