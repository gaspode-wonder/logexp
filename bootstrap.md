# 🚀 Project Bootstrap Script

This script resets your local database, ensures the correct environment variables are set, rebuilds migrations, and applies the schema to a clean PostgreSQL 18 database.

Save this as bootstrap.sh and run it with:
```bash
bash bootstrap.sh
```

```bash
#!/usr/bin/env bash
set -e

echo "=== Bootstrapping LogExp environment ==="

echo ""
echo "1. Ensuring DATABASE_URL is set..."
export DATABASE_URL="postgresql://loginname@localhost:5432/Experiments"
echo "DATABASE_URL set to: $DATABASE_URL"

echo ""
echo "2. Dropping and recreating the Experiments database..."
dropdb -U loginname Experiments --if-exists
createdb -U loginname Experiments
echo "Database recreated."

echo ""
echo "3. Removing old migrations..."
rm -rf migrations/
echo "Old migrations removed."

echo ""
echo "4. Initializing Alembic..."
flask db init
echo "Alembic initialized."

echo ""
echo "5. Generating new migration..."
flask db migrate -m "initial schema for Experiments"
echo "Migration generated."

echo ""
echo "6. Applying migration..."
flask db upgrade
echo "Database schema applied."

echo ""
echo "7. Verifying tables..."
psql -U loginname -d Experiments -c "\dt"

echo ""
echo "✅ Bootstrap complete!"
```