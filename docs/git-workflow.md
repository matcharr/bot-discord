# Git Workflow Guide

Ce document décrit le workflow Git standardisé pour ce projet.

## 🌿 Convention de nommage des branches

### Format
```
type/description-en-kebab-case
```

### Types disponibles
- `feat/` - Nouvelles fonctionnalités
- `fix/` - Corrections de bugs
- `chore/` - Maintenance, dépendances, configuration
- `docs/` - Documentation
- `refactor/` - Refactoring de code
- `test/` - Ajout/modification de tests

### Exemples
```bash
feat/discord-slash-commands
fix/memory-leak-moderation
chore/update-dependencies
docs/api-documentation
refactor/config-system
test/moderation-coverage
```

## 🚀 Créer une nouvelle branche

### Méthode automatique (recommandée)
```bash
./scripts/new-branch.sh feat "add-user-roles"
./scripts/new-branch.sh fix "memory-leak-issue"
```

### Méthode manuelle
```bash
# 1. Aller sur main et mettre à jour
git checkout main
git pull origin main

# 2. Créer la nouvelle branche
git checkout -b feat/ma-nouvelle-fonctionnalite
```

## 📝 Convention de commits

### Format
```
type(scope): description

body (optionnel)

footer (optionnel)
```

### Types
- `feat` - Nouvelle fonctionnalité
- `fix` - Correction de bug
- `docs` - Documentation
- `style` - Formatage, style
- `refactor` - Refactoring
- `test` - Tests
- `chore` - Maintenance

### Exemples
```bash
feat(auth): add user login functionality
fix(moderation): resolve memory leak in warning system
docs: update README with setup instructions
chore(deps): update discord.py to v2.3.2
```

## 🔄 Workflow complet

### 1. Créer une branche
```bash
./scripts/new-branch.sh feat "ma-fonctionnalite"
```

### 2. Développer
```bash
# Faire vos modifications
git add .
git commit -m "feat(scope): description"
```

### 3. Pousser et créer PR
```bash
git push -u origin feat/ma-fonctionnalite
# Créer une Pull Request sur GitHub
```

### 4. Après merge
```bash
git checkout main
git pull origin main
git branch -d feat/ma-fonctionnalite  # Supprimer la branche locale
```

## 🛡️ Hooks Git

### Hooks actifs
- **commit-msg**: Valide le format des messages de commit
- **pre-push**: Valide le nom des branches avant push

### Activer les hooks
```bash
git config core.hooksPath .githooks
```

## 🚫 Branches interdites

Ces noms de branches sont **interdits** :
- `nouvelle-branche`
- `test-branch`
- `temp`
- `wip`
- Tout nom sans préfixe type/

## 🧹 Nettoyage des branches

### Script automatique
```bash
./scripts/cleanup-branches.sh
```

### Commandes manuelles
```bash
# Nettoyer les références distantes
git remote prune origin

# Voir les branches locales mergées
git branch --merged main

# Supprimer les branches locales mergées (sauf main)
git branch --merged main | grep -v "main" | xargs -n 1 git branch -d
```

## 💡 Conseils

### Noms de branches
- Utilisez des tirets, pas d'underscores
- Tout en minuscules
- Soyez descriptifs mais concis
- Évitez les caractères spéciaux

### Messages de commit
- Utilisez l'impératif ("add" pas "added")
- Première ligne max 50 caractères
- Soyez spécifiques sur le scope
- Expliquez le "pourquoi" dans le body si nécessaire

### Pull Requests
- Titre descriptif
- Description claire des changements
- Lier les issues concernées
- Demander une review si nécessaire

### Maintenance régulière
- Nettoyez les branches après chaque merge
- Utilisez `./scripts/cleanup-branches.sh` régulièrement
- Fermez les PRs Dependabot obsolètes sur GitHub