#!/bin/bash
# Development database management script

set -e

# Colors for messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.dev.yml"
DOCKER_COMPOSE="docker compose"
DB_CONTAINER="botdb_dev"

# Utility functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Get timeout command (gtimeout on macOS, timeout on Linux)
get_timeout_cmd() {
    if command -v gtimeout &> /dev/null; then
        echo "gtimeout"
    else
        echo "timeout"
    fi
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    # Use new docker compose syntax if available
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
    else
        DOCKER_COMPOSE="docker-compose"
    fi
}

# Start the database
start_db() {
    log_info "Starting PostgreSQL database..."
    $DOCKER_COMPOSE -f $COMPOSE_FILE up -d postgres

    log_info "Waiting for database to be ready..."
    TIMEOUT_CMD=$(get_timeout_cmd)
    $TIMEOUT_CMD 30 bash -c 'until '$DOCKER_COMPOSE' -f '$COMPOSE_FILE' exec postgres pg_isready -U botuser -d botdb_dev; do sleep 1; done'

    log_success "Database started and ready!"
}

# Stop the database
stop_db() {
    log_info "Stopping database..."
    $DOCKER_COMPOSE -f $COMPOSE_FILE stop postgres
    log_success "Database stopped"
}

# Complete reset (deletes all data)
reset_db() {
    log_warning "⚠️  WARNING: This action will delete ALL development data!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Resetting database..."
        $DOCKER_COMPOSE -f $COMPOSE_FILE down -v
        $DOCKER_COMPOSE -f $COMPOSE_FILE up -d postgres

        log_info "Waiting for database to be ready..."
        TIMEOUT_CMD=$(get_timeout_cmd)
        $TIMEOUT_CMD 30 bash -c 'until '$DOCKER_COMPOSE' -f '$COMPOSE_FILE' exec postgres pg_isready -U botuser -d botdb_dev; do sleep 1; done'

        log_success "Database reset successfully!"
    else
        log_info "Reset cancelled"
    fi
}

# Initialize tables
init_tables() {
    log_info "Initializing tables..."
    init_tables() {
        log_info "Initializing tables..."
        # Load DATABASE_URL from environment or .env file
        if [ -z "$DATABASE_URL" ]; then
            if [ -f .env.development ]; then
                export $(grep -v '^#' .env.development | xargs)
            else
                log_error "DATABASE_URL not set and .env.development not found"
                exit 1
            fi
        fi

        python3 -c "
from project.database.connection import init_database
init_database()
"
    }
    log_success "Tables initialized!"
}

# Show logs
show_logs() {
    $DOCKER_COMPOSE -f $COMPOSE_FILE logs -f postgres
}

# Open psql session
psql_session() {
    log_info "Opening PostgreSQL session..."
    $DOCKER_COMPOSE -f $COMPOSE_FILE exec postgres psql -U botuser -d botdb_dev
}

# Start pgAdmin
start_pgadmin() {
    log_info "Starting pgAdmin..."
    $DOCKER_COMPOSE -f $COMPOSE_FILE --profile admin up -d pgadmin
    log_success "pgAdmin available at http://localhost:8080"
    log_info "Email: admin@bot.local | Password: admin"
}

# Show status
status() {
    log_info "Services status:"
    $DOCKER_COMPOSE -f $COMPOSE_FILE ps
}

# Show help
show_help() {
    echo "🤖 Discord bot database management script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start PostgreSQL"
    echo "  stop        Stop PostgreSQL"
    echo "  restart     Restart PostgreSQL"
    echo "  reset       Complete reset (deletes all data)"
    echo "  init        Initialize tables"
    echo "  logs        Show logs"
    echo "  psql        Open PostgreSQL session"
    echo "  pgadmin     Start pgAdmin (web interface)"
    echo "  status      Show services status"
    echo "  help        Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 start && $0 init    # Start and initialize"
    echo "  $0 reset && $0 init    # Complete reset"
    echo "  $0 psql                # Interactive session"
}

# Main
main() {
    check_docker

    case "${1:-help}" in
        start)
            start_db
            ;;
        stop)
            stop_db
            ;;
        restart)
            stop_db
            start_db
            ;;
        reset)
            reset_db
            ;;
        init)
            init_tables
            ;;
        logs)
            show_logs
            ;;
        psql)
            psql_session
            ;;
        pgadmin)
            start_pgadmin
            ;;
        status)
            status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
