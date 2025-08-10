#!/bin/bash
# Script pour configurer les hooks Git et pre-commit
# Usage: ./scripts/setup-git-hooks.sh

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Configuration des hooks Git${NC}"
echo ""

# 1. Configurer le chemin des hooks Git
echo -e "${YELLOW}📁 Configuration du chemin des hooks...${NC}"
git config core.hooksPath .githooks
echo -e "${GREEN}✅ Hooks configurés dans .githooks/${NC}"

# 2. Rendre les hooks exécutables
echo -e "${YELLOW}🔐 Configuration des permissions...${NC}"
chmod +x .githooks/*
echo -e "${GREEN}✅ Permissions configurées${NC}"

# 3. Installer pre-commit si disponible
if command -v pre-commit &> /dev/null; then
    echo -e "${YELLOW}🔄 Installation des hooks pre-commit...${NC}"
    pre-commit install
    echo -e "${GREEN}✅ Pre-commit hooks installés${NC}"
else
    echo -e "${YELLOW}⚠️  Pre-commit non trouvé. Installation optionnelle :${NC}"
    echo "   pip install pre-commit"
    echo "   pre-commit install"
fi

echo ""
echo -e "${BLUE}📋 Hooks actifs :${NC}"
echo -e "${GREEN}• commit-msg${NC} - Valide le format des messages de commit"
echo -e "${GREEN}• pre-push${NC} - Valide le nom des branches"
if command -v pre-commit &> /dev/null; then
    echo -e "${GREEN}• pre-commit${NC} - Linting et formatage automatique"
fi

echo ""
echo -e "${BLUE}💡 Test des hooks :${NC}"
echo "• Créer une branche : ./scripts/new-branch.sh feat \"test-hooks\""
echo "• Faire un commit : git commit -m \"feat(test): message de test\""

echo ""
echo -e "${GREEN}🎉 Configuration terminée !${NC}"