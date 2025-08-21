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
    if command -v "$1" &> /dev/null; then
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

# Enhanced Docker Compose detection with better error handling
detect_docker_compose() {
    ((CHECKS_TOTAL++))

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed - Docker Compose unavailable"
        DOCKER_CMD=""
        return 1
    fi

    # Test docker compose (newer syntax)
    if docker compose version &> /dev/null 2>&1; then
        log_success "docker compose (v2) is available"
        DOCKER_CMD="docker compose"
        return 0
    fi

    # Test docker-compose (legacy syntax)
    if command -v docker-compose &> /dev/null && docker-compose version &> /dev/null 2>&1; then
        log_success "docker-compose (legacy) is available"
        DOCKER_CMD="docker-compose"
        return 0
    fi

    # Docker is available but compose is not
    log_error "Docker Compose is not available"
    log_info "  💡 Install Docker Compose: https://docs.docker.com/compose/install/"
    DOCKER_CMD=""
    return 1
}

# Detect Docker Compose availability
detect_docker_compose
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
    log_success "Script db-manage.sh is executable"
else
    log_error "Script db-manage.sh is not executable"
fi

# 6. Database connection test
log_info "6. Database connection test..."

# Test Docker PostgreSQL first if Docker Compose is available
test_docker_database() {
    if [ -z "$DOCKER_CMD" ]; then
        return 1
    fi

    ((CHECKS_TOTAL++))

    # Check if PostgreSQL container is running
    if ! $DOCKER_CMD -f docker-compose.dev.yml ps postgres 2>/dev/null | grep -q "Up"; then
        log_warning "PostgreSQL Docker container is not running"
        log_info "  💡 Start with: ./scripts/db-manage.sh start"
        return 1
    fi

    log_success "PostgreSQL Docker container is running"

    # Test database connection
    ((CHECKS_TOTAL++))
    local connection_test
    if connection_test=$(timeout 10 "$DOCKER_CMD" -f docker-compose.dev.yml exec -T postgres pg_isready -U botuser -d botdb_dev 2>&1); then
        log_success "PostgreSQL Docker connection successful"
        return 0
    else
        log_error "PostgreSQL Docker connection failed"
        log_info "  💡 Error: $connection_test"
        log_info "  💡 Try: ./scripts/db-manage.sh reset"
        return 1
    fi
}

# Test native PostgreSQL installation
test_native_database() {
    ((CHECKS_TOTAL++))

    if ! command -v psql &> /dev/null; then
        log_warning "psql command not found - native PostgreSQL not available"
        return 1
    fi

    # Test connection to native PostgreSQL
    local connection_test
    if connection_test=$(timeout 10 psql -U botuser -d botdb_dev -h localhost -c "SELECT 1;" 2>&1); then
        log_success "Native PostgreSQL connection successful"
        return 0
    else
        log_warning "Native PostgreSQL connection failed"
        log_info "  💡 Error: $connection_test"
        log_info "  💡 See: docs/setup-no-docker.md"
        return 1
    fi
}

# Try Docker first, then native PostgreSQL
if ! test_docker_database; then
    if ! test_native_database; then
        ((CHECKS_TOTAL++))
        log_error "No working PostgreSQL database found"
        log_info "  💡 Options:"
        log_info "    - Docker: ./scripts/db-manage.sh start"
        log_info "    - Native: see docs/setup-no-docker.md"
    fi
fi

# 7. Python imports test
log_info "7. Testing project imports..."
((CHECKS_TOTAL++))

# Function to test Python imports with better error handling
test_python_imports() {
    local import_result
    local exit_code
    # Execute Python import test with proper error handling
    import_result=$(python3 -c "
import sys
import os
# Use absolute path and validate it exists
project_path = os.path.abspath('project')
if not os.path.isdir(project_path):
    print('ERROR: Project directory not found')
    sys.exit(2)
sys.path.insert(0, project_path)
try:
    from database.models import SecureWarning
    from database.services import WarningService
    from database.security import SecurityManager
    print('SUCCESS: All imports work')
except ImportError as e:
    print('IMPORT_ERROR: ' + str(e))
    sys.exit(1)
except Exception as e:
    print('ERROR: ' + str(e))
    sys.exit(2)
" 2>&1)
    exit_code=$?

    # Parse results and provide clear feedback
    case $exit_code in
        0)
            if echo "$import_result" | grep -q "SUCCESS"; then
                log_success "All project imports work correctly"
                return 0
            else
                log_error "Unexpected success result: $import_result"
                return 1
            fi
            ;;
        1)
            # Import error - extract the specific import that failed
            local import_error
            import_error=$(echo "$import_result" | grep "IMPORT_ERROR:" | sed 's/IMPORT_ERROR: //')
            log_error "Import failed: $import_error"
            log_info "  💡 Try: pip install -r requirements.txt"
            return 1
            ;;
        2)
            # Other Python error
            local python_error
            python_error=$(echo "$import_result" | grep "ERROR:" | sed 's/ERROR: //')
            log_error "Python execution error: $python_error"
            log_info "  💡 Check Python environment and project structure"
            return 1
            ;;
        *)
            # Unexpected exit code
            log_error "Unexpected error during import test (exit code: $exit_code)"
            log_error "Output: $import_result"
            return 1
            ;;
    esac
}

# Execute the import test
test_python_imports
# Function to show final summary and exit
show_final_summary() {
    echo ""
    echo "📊 Verification Summary"
    echo "============================"
    echo -e "Tests passed: ${GREEN}$CHECKS_PASSED${NC}/$CHECKS_TOTAL"

    if [ $CHECKS_PASSED -eq $CHECKS_TOTAL ]; then
        echo -e "${GREEN}🎉 Environment perfectly configured!${NC}"
        exit 0
    elif [ $CHECKS_PASSED -gt $((CHECKS_TOTAL * 3 / 4)) ]; then
        echo -e "${YELLOW}⚠️  Environment mostly configured, some adjustments needed${NC}"
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
}

# Call the summary function at the end
show_final_summary
