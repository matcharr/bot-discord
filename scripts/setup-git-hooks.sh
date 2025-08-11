#!/bin/bash
# Script to configure Git hooks and pre-commit
# Usage: ./scripts/setup-git-hooks.sh

set -e

# Colors for display
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Git Hooks Configuration${NC}"
echo ""

# 1. Configure Git hooks path
echo -e "${YELLOW}📁 Configuring hooks path...${NC}"
git config core.hooksPath .githooks
echo -e "${GREEN}✅ Hooks configured in .githooks/${NC}"

# 2. Make hooks executable
echo -e "${YELLOW}🔐 Setting permissions...${NC}"
chmod +x .githooks/*
echo -e "${GREEN}✅ Permissions configured${NC}"

# 3. Install pre-commit if available
if command -v pre-commit &> /dev/null; then
    echo -e "${YELLOW}🔄 Installing pre-commit hooks...${NC}"
    pre-commit install
    echo -e "${GREEN}✅ Pre-commit hooks installed${NC}"
else
    echo -e "${YELLOW}⚠️  Pre-commit not found. Optional installation:${NC}"
    echo "   pip install pre-commit"
    echo "   pre-commit install"
fi

echo ""
echo -e "${BLUE}📋 Active hooks:${NC}"
echo -e "${GREEN}• commit-msg${NC} - Validates commit message format"
echo -e "${GREEN}• pre-push${NC} - Validates branch names"
if command -v pre-commit &> /dev/null; then
    echo -e "${GREEN}• pre-commit${NC} - Automatic linting and formatting"
fi

echo ""
echo -e "${BLUE}💡 Testing hooks:${NC}"
echo "• Create branch: ./scripts/new-branch.sh feat \"test-hooks\""
echo "• Make commit: git commit -m \"feat(test): test message\""

echo ""
echo -e "${GREEN}🎉 Configuration completed!${NC}"