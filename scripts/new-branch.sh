#!/bin/bash
# Script pour créer une nouvelle branche avec convention de nommage
# Usage: ./scripts/new-branch.sh <type> <description>
# Exemple: ./scripts/new-branch.sh feat "add-user-roles"

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction d'aide
show_help() {
    echo "Usage: $0 <type> <description>"
    echo ""
    echo "Types disponibles:"
    echo "  feat      - Nouvelle fonctionnalité"
    echo "  fix       - Correction de bug"
    echo "  chore     - Maintenance, dépendances"
    echo "  docs      - Documentation"
    echo "  refactor  - Refactoring de code"
    echo "  test      - Tests"
    echo ""
    echo "Exemples:"
    echo "  $0 feat \"add-user-roles\""
    echo "  $0 fix \"memory-leak-moderation\""
    echo "  $0 chore \"update-dependencies\""
}

# Vérification des arguments
if [ $# -ne 2 ]; then
    echo -e "${RED}❌ Erreur: Il faut exactement 2 arguments${NC}"
    show_help
    exit 1
fi

TYPE=$1
DESCRIPTION=$2

# Types valides
VALID_TYPES=("feat" "fix" "chore" "docs" "refactor" "test")

# Vérifier que le type est valide
if [[ ! " ${VALID_TYPES[@]} " =~ " ${TYPE} " ]]; then
    echo -e "${RED}❌ Type invalide: $TYPE${NC}"
    echo -e "${YELLOW}Types valides: ${VALID_TYPES[*]}${NC}"
    exit 1
fi

# Nettoyer la description (remplacer espaces par tirets, minuscules)
CLEAN_DESCRIPTION=$(echo "$DESCRIPTION" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')

# Nom de la branche
BRANCH_NAME="${TYPE}/${CLEAN_DESCRIPTION}"

echo -e "${YELLOW}🔄 Création de la branche: $BRANCH_NAME${NC}"

# Vérifier qu'on n'est pas déjà sur cette branche
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "$BRANCH_NAME" ]; then
    echo -e "${RED}❌ Vous êtes déjà sur la branche $BRANCH_NAME${NC}"
    exit 1
fi

# Vérifier que la branche n'existe pas déjà
if git show-ref --verify --quiet refs/heads/$BRANCH_NAME; then
    echo -e "${RED}❌ La branche $BRANCH_NAME existe déjà${NC}"
    exit 1
fi

# Sauvegarder les changements non commitées s'il y en a
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}💾 Sauvegarde des changements non commitées...${NC}"
    git stash push -m "Auto-stash before creating branch $BRANCH_NAME"
    STASHED=true
else
    STASHED=false
fi

# Aller sur main et mettre à jour
echo -e "${YELLOW}🔄 Mise à jour de la branche main...${NC}"
git checkout main
git pull origin main

# Créer et basculer sur la nouvelle branche
echo -e "${YELLOW}🌿 Création de la branche $BRANCH_NAME...${NC}"
git checkout -b "$BRANCH_NAME"

# Restaurer les changements si nécessaire
if [ "$STASHED" = true ]; then
    echo -e "${YELLOW}📦 Restauration des changements sauvegardés...${NC}"
    git stash pop
fi

echo -e "${GREEN}✅ Branche $BRANCH_NAME créée avec succès !${NC}"
echo -e "${GREEN}📍 Vous êtes maintenant sur la branche $BRANCH_NAME${NC}"
echo ""
echo -e "${YELLOW}Prochaines étapes:${NC}"
echo "1. Faire vos modifications"
echo "2. git add ."
echo "3. git commit -m \"${TYPE}(scope): description\""
echo "4. git push -u origin $BRANCH_NAME"