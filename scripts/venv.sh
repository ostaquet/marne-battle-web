#!/bin/bash
# Clean and create virtual environment with all dependencies

set -e  # Exit on first error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "========================================="
echo "Setting up virtual environment"
echo "========================================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Show Python version
PYTHON_VERSION=$(python3 --version)
echo -e "${BLUE}Using: $PYTHON_VERSION${NC}"
echo ""

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}Removing existing virtual environment...${NC}"
    rm -rf venv
    echo -e "${GREEN}✓ Removed old venv${NC}"
    echo ""
fi

# Create new virtual environment
echo -e "${YELLOW}Creating new virtual environment...${NC}"
python3 -m venv venv
echo -e "${GREEN}✓ Virtual environment created${NC}"
echo ""

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip -q
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}Installing dependencies from requirements.txt...${NC}"
pip install -r requirements.txt -q
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Show installed packages
echo -e "${BLUE}Installed packages:${NC}"
pip list --format=columns

echo ""
echo "========================================="
echo -e "${GREEN}Virtual environment ready!${NC}"
echo "========================================="
echo ""
echo "To activate the virtual environment, run:"
echo -e "${BLUE}source venv/bin/activate${NC}"
