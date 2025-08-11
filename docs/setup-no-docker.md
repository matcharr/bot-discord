# Setup without Docker 🚀

Guide to configure the development environment without Docker.

## Native PostgreSQL Installation

### macOS (Homebrew)
```bash
# Install PostgreSQL
brew install postgresql@15

# Start the service
brew services start postgresql@15

# Create the database
createdb botdb_dev

# Create the user
psql postgres -c "CREATE USER botuser WITH PASSWORD 'devpassword';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE botdb_dev TO botuser;"
```

### Linux (Ubuntu/Debian)
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start the service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres createdb botdb_dev
sudo -u postgres psql -c "CREATE USER botuser WITH PASSWORD 'devpassword';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE botdb_dev TO botuser;"
```

### Windows
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Install with default settings
3. Use pgAdmin or psql to create the database:
```sql
CREATE DATABASE botdb_dev;
CREATE USER botuser WITH PASSWORD 'devpassword';
GRANT ALL PRIVILEGES ON DATABASE botdb_dev TO botuser;
```

## Configuration

### 1. Environment Variables
Modify `.env.development`:
```bash
# Local PostgreSQL (without Docker)
DATABASE_URL=postgresql://botuser:devpassword@localhost:5432/botdb_dev

# Rest remains the same...
ENCRYPTION_KEY=dev_fernet_key_base64_encoded_replace_in_production
SALT_KEY=ZGV2X3NhbHRfa2V5XzEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg=
PEPPER_KEY=ZGV2X3BlcHBlcl9rZXlfMTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3
```

### 2. Simplified Management Script
```bash
# Create a simple management script
cat > scripts/db-native.sh << 'EOF'
#!/bin/bash

case "$1" in
    start)
        # macOS
        brew services start postgresql@15 2>/dev/null || \
        # Linux
        sudo systemctl start postgresql 2>/dev/null || \
        echo "Start PostgreSQL manually"
        ;;
    stop)
        brew services stop postgresql@15 2>/dev/null || \
        sudo systemctl stop postgresql 2>/dev/null || \
        echo "Stop PostgreSQL manually"
        ;;
    psql)
        psql -U botuser -d botdb_dev -h localhost
        ;;
    init)
        python3 -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://botuser:devpassword@localhost:5432/botdb_dev'
from project.database.connection import init_database
init_database()
"
        ;;
    *)
        echo "Usage: $0 {start|stop|psql|init}"
        ;;
esac
EOF

chmod +x scripts/db-native.sh
```

## Testing and Verification

```bash
# Test the connection
psql -U botuser -d botdb_dev -h localhost -c "SELECT version();"

# Initialize tables
./scripts/db-native.sh init

# Run tests
python -m pytest tests/database/ -v
```

## Updated Makefile Commands

Add to Makefile:
```makefile
# Alternative without Docker
db-native-start: ## Start native PostgreSQL
	./scripts/db-native.sh start

db-native-init: ## Initialize native PostgreSQL
	./scripts/db-native.sh init

db-native-psql: ## Connect to native PostgreSQL
	./scripts/db-native.sh psql
```

## Advantages of Native Approach

✅ **Faster** - No Docker overhead  
✅ **Simpler** - Single installation  
✅ **Fewer resources** - No containers  
✅ **IDE integration** - Direct connection possible  

## Disadvantages

❌ **Less isolated** - Shared with other projects  
❌ **Different setup** - OS dependent  
❌ **Manual cleanup** - No automatic reset  

## Migration to Docker Later

If you want to return to Docker later:
1. Export data: `pg_dump botdb_dev > backup.sql`
2. Setup Docker: `./scripts/db-manage.sh start`
3. Import: `psql -U botuser -d botdb_dev < backup.sql`