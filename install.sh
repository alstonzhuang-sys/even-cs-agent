#!/bin/bash
# install.sh - Automated installation script for Even CS Agent
#
# Interactive mode (default):
#   ./install.sh
#
# Non-interactive mode (for automation):
#   FEISHU_ID=ou_xxx GEMINI_API_KEY=your_key ./install.sh

set -e  # Exit on error

echo "=========================================="
echo "  Even CS Agent - Installation Script"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Python version
echo "Step 1: Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
echo ""

# Step 2: Install dependencies
echo "Step 2: Installing Python dependencies..."
if pip3 install -r requirements.txt; then
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Step 3: Copy configuration template
echo "Step 3: Setting up configuration..."
if [ ! -f config/channels.json ]; then
    cp config/channels.json.example config/channels.json
    echo -e "${GREEN}✅ Configuration file created${NC}"
else
    echo -e "${YELLOW}⚠️  config/channels.json already exists, skipping${NC}"
fi
echo ""

# Step 4: Configure Feishu ID
echo "Step 4: Configuring Rosen's Feishu ID..."
feishu_id="${FEISHU_ID:-}"

if [ -z "$feishu_id" ]; then
    # Interactive mode
    echo -e "${YELLOW}Please enter Rosen's Feishu ID (format: ou_xxx):${NC}"
    read -p "> " feishu_id
fi

if [ -z "$feishu_id" ]; then
    echo -e "${RED}❌ Feishu ID cannot be empty${NC}"
    exit 1
fi

# Replace placeholder in config
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/ou_xxx/$feishu_id/g" config/channels.json
else
    sed -i "s/ou_xxx/$feishu_id/g" config/channels.json
fi

echo -e "${GREEN}✅ Feishu ID configured: $feishu_id${NC}"
echo ""

# Step 5: Configure API key
echo "Step 5: Setting up Gemini API key..."
api_key="${GEMINI_API_KEY:-}"

if [ -z "$api_key" ]; then
    # Interactive mode
    echo -e "${YELLOW}Please enter your Gemini API key:${NC}"
    read -s -p "> " api_key
    echo ""
fi

if [ -z "$api_key" ]; then
    echo -e "${RED}❌ API key cannot be empty${NC}"
    exit 1
fi

# Detect shell
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.profile"
fi

# Add to shell profile if not already present
if ! grep -q "GEMINI_API_KEY" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Even CS Agent - Gemini API Key" >> "$SHELL_RC"
    echo "export GEMINI_API_KEY='$api_key'" >> "$SHELL_RC"
    echo -e "${GREEN}✅ API key added to $SHELL_RC${NC}"
else
    echo -e "${YELLOW}⚠️  GEMINI_API_KEY already in $SHELL_RC, skipping${NC}"
fi

# Set for current session
export GEMINI_API_KEY="$api_key"
echo ""

# Step 6: Verify installation
echo "Step 6: Verifying installation..."
if python3 scripts/health_check.py; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "  ✅ Installation Complete!"
    echo "==========================================${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Reload your shell: source $SHELL_RC"
    echo "2. Test the agent: ./test_all.sh"
    echo "3. Read SKILL.md for OpenClaw integration"
    echo ""
else
    echo ""
    echo -e "${RED}=========================================="
    echo "  ❌ Installation Failed"
    echo "==========================================${NC}"
    echo ""
    echo "Please check the errors above and try again."
    echo "For help, see: https://github.com/alstonzhuang-sys/even-cs-agent/issues"
    echo ""
    exit 1
fi

