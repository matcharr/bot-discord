#!/bin/bash
# Complete development environment verification script

# set -e # Removed to allow continuation even on errors

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
CHECKS_PASSED=0
CHECKS_TOTAL=0

# Utility functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((CHECKS_PASSED++))
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_command() {
    ((CHECKS_TOTAL++))
    if command -v $1 &> /dev/null; then
        log_success "$1 is installed"
        return 0
    else
        log_error "$1 is not installed"
        return 1
    fi
}

check_python_package() {
    ((CHECKS_TOTAL++))
    if python3 -c "import $1" &> /dev/null; then
        log_success "Python package '$1' available"
        return 0
    else
        log_error "Python package '$1' missing"
        return 1
    fi
}

check_file() {
    ((CHECKS_TOTAL++))
    if [ -f "$1" ]; then
        log_success "File '$1' exists"
        return 0
    else
        log_error "File '$1' missing"
        return 1
    fi
}

check_directory() {
    ((CHECKS_TOTAL++))
    if [ -d "$1" ]; then
        log_success "Directory '$1' exists"
        return 0
    else
        log_error "Directory '$1' missing"
        return 1
    fi
}

echo "🔍 Development environment verification"
echo "======================================"

# 1. System tools verification
log_info "1. System tools verification..."
check_command "python3"
if command -v pip3 &> /dev/null; then
    ((CHECKS_TOTAL++))
    log_success "pip3 is installed"
elif command -v pip &> /dev/null; then
    ((CHECKS_TOTAL++))
    log_success "pip is installed"
else
    ((CHECKS_TOTAL++))
    log_error "pip/pip3 is not installed"
fi
check_command "docker"
((CHECKS_TOTAL++))
if docker compose version &> /dev/null; then
    log_success "docker compose is available"
elif command -v docker-compose &> /dev/null; then
    log_success "docker-compose is available"
else
    log_error "docker compose/docker-compose is not available"
fi
check_command "git"

# 2. Essential Python packages verification
log_info "2. Python packages verification..."
check_python_package "sqlalchemy"
check_python_package "psycopg2"
check_python_package "cryptography"
check_python_package "pytest"
check_python_package "discord"

# 3. Project structure verification
log_info "3. Project structure verification..."
check_directory "project"
check_directory "project/database"
check_directory "tests"
check_directory "tests/database"
check_directory "scripts"
check_directory "docs"

# 4. Essential files verification
log_info "4. Essential files verification..."
check_file "project/database/models.py"
check_file "project/database/services.py"
check_file "project/database/security.py"
check_file "project/database/connection.py"
check_file "docker-compose.dev.yml"
check_file "scripts/db-manage.sh"
check_file ".env.development"
check_file ".env.test"

# 5. Script permissions verification
log_info "5. Permissions verification..."
((CHECKS_TOTAL++))
if [ -x "scripts/db-manage.sh" ]; then
    log_success "Script db-manage.sh est exécutable"
else
    log_error "Script db-manage.sh n'est pas exécutable"
fi

# 6. Test de la base de données
log_info "6. Test de la base de données..."
((CHECKS_TOTAL++))

# Test Docker d'abord
if command -v docker &> /dev/null && docker-compose -f docker-compose.dev.yml ps postgres 2>/dev/null | grep -q "Up"; then
    log_success "PostgreSQL Docker est en cours d'exécution"
    
    # Test de connexion Docker
    ((CHECKS_TOTAL++))
    if timeout 5 docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U botuser -d botdb_dev &> /dev/null; then
        log_success "Connexion PostgreSQL Docker OK"
    else
        log_error "Impossible de se connecter à PostgreSQL Docker"
    fi
# Test PostgreSQL natif
elif command -v psql &> /dev/null && timeout 5 psql -U botuser -d botdb_dev -h localhost -c "SELECT 1;" &> /dev/null; then
    log_success "PostgreSQL natif fonctionne"
else
    log_warning "PostgreSQL non détecté (Docker ou natif)"
    log_info "  - Docker: ./scripts/db-manage.sh start"
    log_info "  - Natif: voir docs/SETUP_NO_DOCKER.md"
fi

# 7. Python imports test
log_info "7. Testing project imports..."
((CHECKS_TOTAL++))
if python3 -c "
import sys
sys.path.append('project')
from database.models import SecureWarning
from database.services import WarningService
from database.security import SecurityManager
print('Imports OK')
" &> /dev/null; then
    log_success "Project imports work"
else
    log_error "Error in project imports"
fi

# 8. Test des variables d'environnement
log_info "8. Test des variables d'environnement..."
((CHECKS_TOTAL++))
if [ -f ".env.development" ]; then
    source .env.development
    if [ ! -z "$DATABASE_URL" ] && [ ! -z "$ENCRYPTION_KEY" ]; then
        log_success "Environment variables configured"
    else
        log_error "Missing environment variables in .env.development"
    fi
else
    log_error "Missing .env.development file"
fi

# 9. Test rapide des tests unitaires (si possible)
log_info "9. Test rapide des tests unitaires..."
((CHECKS_TOTAL++))
if timeout 30 python3 -m pytest tests/database/test_security.py -v &> /dev/null; then
    log_success "Basic unit tests work"
else
    log_warning "Unit tests fail or take too long"
fi

# Résumé
echo ""
echo "📊 Résumé de la vérification"
echo "============================"
echo -e "Tests passés: ${GREEN}$CHECKS_PASSED${NC}/$CHECKS_TOTAL"

if [ $CHECKS_PASSED -eq $CHECKS_TOTAL ]; then
    echo -e "${GREEN}🎉 Environnement parfaitement configuré !${NC}"
    exit 0
elif [ $CHECKS_PASSED -gt $((CHECKS_TOTAL * 3 / 4)) ]; then
    echo -e "${YELLOW}⚠️  Environnement majoritairement configuré, quelques ajustements nécessaires${NC}"
    exit 0
else
    echo -e "${RED}❌ Environment requires significant corrections${NC}"
    echo ""
    echo "💡 Suggestions:"
    echo "  - Install missing dependencies"
    echo "  - Start database: ./scripts/db-manage.sh start"
    echo "  - Check configuration: docs/SETUP_CHECKLIST.md"
    exit 1
fi