#!/bin/bash
# Script to clean up obsolete Git branches
# Usage: ./scripts/cleanup-branches.sh

set -e

# Colors for display
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Git Branch Cleanup${NC}"
echo ""

# 1. Clean remote references
echo -e "${YELLOW}🔄 Cleaning obsolete remote references...${NC}"
PRUNED=$(git remote prune origin 2>&1)
if echo "$PRUNED" | grep -q "pruned"; then
    echo "$PRUNED" | grep "pruned" | wc -l | xargs -I {} echo -e "${GREEN}✅ {} remote references removed${NC}"
else
    echo -e "${GREEN}✅ No obsolete references found${NC}"
fi
echo ""

# 2. Show merged local branches
echo -e "${YELLOW}📋 Local branches merged into main:${NC}"
MERGED_BRANCHES=$(git branch --merged main | grep -v "main" | grep -v "\*" | sed 's/^[ ]*//')
if [ -z "$MERGED_BRANCHES" ]; then
    echo -e "${GREEN}✅ No merged local branches to delete${NC}"
else
    echo "$MERGED_BRANCHES" | while read branch; do
        echo -e "  ${YELLOW}📌 $branch${NC}"
    done
    echo ""
    
    # Ask for confirmation
    echo -e "${YELLOW}❓ Do you want to delete these branches? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "$MERGED_BRANCHES" | while read branch; do
            git branch -d "$branch"
            echo -e "${GREEN}✅ Branch $branch deleted${NC}"
        done
    else
        echo -e "${BLUE}ℹ️  Branches kept${NC}"
    fi
fi
echo ""

# 3. Show remaining Dependabot remote branches
echo -e "${YELLOW}🤖 Remaining Dependabot branches on GitHub:${NC}"
DEPENDABOT_BRANCHES=$(git branch -r | grep "dependabot" | sed 's/^[ ]*//')
if [ -z "$DEPENDABOT_BRANCHES" ]; then
    echo -e "${GREEN}✅ No remaining Dependabot branches${NC}"
else
    echo "$DEPENDABOT_BRANCHES" | while read branch; do
        echo -e "  ${YELLOW}🤖 $branch${NC}"
    done
    echo ""
    echo -e "${BLUE}ℹ️  These branches can be closed manually on GitHub${NC}"
fi
echo ""

# 4. Final summary
echo -e "${BLUE}📊 Current branch summary:${NC}"
echo -e "${GREEN}Local branches:${NC}"
git branch | sed 's/^/  /'
echo ""
echo -e "${GREEN}Active remote branches:${NC}"
git branch -r | grep -v "dependabot" | sed 's/^/  /'

echo ""
echo -e "${GREEN}🎉 Cleanup completed!${NC}"