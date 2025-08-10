#!/bin/bash
# Script pour nettoyer les branches Git obsolètes
# Usage: ./scripts/cleanup-branches.sh

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Nettoyage des branches Git${NC}"
echo ""

# 1. Nettoyer les références distantes
echo -e "${YELLOW}🔄 Nettoyage des références distantes obsolètes...${NC}"
PRUNED=$(git remote prune origin 2>&1)
if echo "$PRUNED" | grep -q "pruned"; then
    echo "$PRUNED" | grep "pruned" | wc -l | xargs -I {} echo -e "${GREEN}✅ {} références distantes supprimées${NC}"
else
    echo -e "${GREEN}✅ Aucune référence obsolète trouvée${NC}"
fi
echo ""

# 2. Afficher les branches locales mergées
echo -e "${YELLOW}📋 Branches locales mergées dans main :${NC}"
MERGED_BRANCHES=$(git branch --merged main | grep -v "main" | grep -v "\*" | sed 's/^[ ]*//')
if [ -z "$MERGED_BRANCHES" ]; then
    echo -e "${GREEN}✅ Aucune branche locale mergée à supprimer${NC}"
else
    echo "$MERGED_BRANCHES" | while read branch; do
        echo -e "  ${YELLOW}📌 $branch${NC}"
    done
    echo ""
    
    # Demander confirmation
    echo -e "${YELLOW}❓ Voulez-vous supprimer ces branches ? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "$MERGED_BRANCHES" | while read branch; do
            git branch -d "$branch"
            echo -e "${GREEN}✅ Branche $branch supprimée${NC}"
        done
    else
        echo -e "${BLUE}ℹ️  Branches conservées${NC}"
    fi
fi
echo ""

# 3. Afficher les branches distantes Dependabot restantes
echo -e "${YELLOW}🤖 Branches Dependabot restantes sur GitHub :${NC}"
DEPENDABOT_BRANCHES=$(git branch -r | grep "dependabot" | sed 's/^[ ]*//')
if [ -z "$DEPENDABOT_BRANCHES" ]; then
    echo -e "${GREEN}✅ Aucune branche Dependabot restante${NC}"
else
    echo "$DEPENDABOT_BRANCHES" | while read branch; do
        echo -e "  ${YELLOW}🤖 $branch${NC}"
    done
    echo ""
    echo -e "${BLUE}ℹ️  Ces branches peuvent être fermées manuellement sur GitHub${NC}"
fi
echo ""

# 4. Résumé final
echo -e "${BLUE}📊 Résumé des branches actuelles :${NC}"
echo -e "${GREEN}Branches locales :${NC}"
git branch | sed 's/^/  /'
echo ""
echo -e "${GREEN}Branches distantes actives :${NC}"
git branch -r | grep -v "dependabot" | sed 's/^/  /'

echo ""
echo -e "${GREEN}🎉 Nettoyage terminé !${NC}"