#!/bin/bash
# Script to create a new branch with naming convention
# Usage: ./scripts/new-branch.sh <type> <description>
# Example: ./scripts/new-branch.sh feat "add-user-roles"

set -e

# Colors for display
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Help function
show_help() {
    echo "Usage: $0 <type> <description>"
    echo ""
    echo "Available types:"
    echo "  feat      - New feature"
    echo "  fix       - Bug fix"
    echo "  chore     - Maintenance, dependencies"
    echo "  docs      - Documentation"
    echo "  refactor  - Code refactoring"
    echo "  test      - Tests"
    echo ""
    echo "Examples:"
    echo "  $0 feat \"add-user-roles\""
    echo "  $0 fix \"memory-leak-moderation\""
    echo "  $0 chore \"update-dependencies\""
}

# Argument validation
if [ $# -ne 2 ]; then
    echo -e "${RED}❌ Error: Exactly 2 arguments required${NC}"
    show_help
    exit 1
fi

TYPE=$1
DESCRIPTION=$2

# Valid types
VALID_TYPES=("feat" "fix" "chore" "docs" "refactor" "test")

# Verify type is valid
if [[ ! " ${VALID_TYPES[@]} " =~ " ${TYPE} " ]]; then
    echo -e "${RED}❌ Invalid type: $TYPE${NC}"
    echo -e "${YELLOW}Valid types: ${VALID_TYPES[*]}${NC}"
    exit 1
fi

# Clean description (replace spaces with dashes, lowercase)
CLEAN_DESCRIPTION=$(echo "$DESCRIPTION" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')

# Branch name
BRANCH_NAME="${TYPE}/${CLEAN_DESCRIPTION}"

echo -e "${YELLOW}🔄 Creating branch: $BRANCH_NAME${NC}"

# Check we're not already on this branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "$BRANCH_NAME" ]; then
    echo -e "${RED}❌ Already on branch $BRANCH_NAME${NC}"
    exit 1
fi

# Check branch doesn't already exist
if git show-ref --verify --quiet refs/heads/$BRANCH_NAME; then
    echo -e "${RED}❌ Branch $BRANCH_NAME already exists${NC}"
    exit 1
fi

# Save uncommitted changes if any
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}💾 Saving uncommitted changes...${NC}"
    git stash push -m "Auto-stash before creating branch $BRANCH_NAME"
    STASHED=true
else
    STASHED=false
fi

# Switch to main and update
echo -e "${YELLOW}🔄 Updating main branch...${NC}"
git checkout main
git pull origin main

# Create and switch to new branch
echo -e "${YELLOW}🌿 Creating branch $BRANCH_NAME...${NC}"
git checkout -b "$BRANCH_NAME"

# Restore changes if necessary
if [ "$STASHED" = true ]; then
    echo -e "${YELLOW}📦 Restoring saved changes...${NC}"
    git stash pop
fi

echo -e "${GREEN}✅ Branch $BRANCH_NAME created successfully!${NC}"
echo -e "${GREEN}📍 You are now on branch $BRANCH_NAME${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Make your changes"
echo "2. git add ."
echo "3. git commit -m \"${TYPE}(scope): description\""
echo "4. git push -u origin $BRANCH_NAME"