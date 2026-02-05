# Alembic Database Migrations

This directory contains Alembic database migration scripts for the CISO Digital Risk Assessment platform.

## 📋 Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [Common Commands](#common-commands)
- [Creating New Migrations](#creating-new-migrations)
- [Testing Migrations](#testing-migrations)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

**Alembic** is a lightweight database migration tool for SQLAlchemy. It allows us to:

- **Track schema changes** over time with version control
- **Apply migrations** incrementally (upgrade)
- **Rollback changes** if needed (downgrade)
- **Autogenerate migrations** from SQLAlchemy model changes
- **Maintain multiple environments** (dev, staging, production)

### Key Features of Our Setup

✅ **Async SQLAlchemy support** - Works with our async database engine  
✅ **PostgreSQL + SQLite compatibility** - Migrations work on both databases  
✅ **Auto-formatting** - Black formats migration files automatically  
✅ **Type comparison** - Detects column type changes  
✅ **Default value tracking** - Detects server default changes  

---

## Setup

Alembic is already configured in this project. If you're setting up a new environment:

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `alembic==1.13.1`
- `sqlalchemy==2.0.25`
- `asyncpg` (PostgreSQL async driver)
- `aiosqlite` (SQLite async driver)

### 2. Configure Database URL

Set your `DATABASE_URL` environment variable:

```bash
# PostgreSQL (Production/Staging)
export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/ciso_digital"

# SQLite (Development/Testing)
export DATABASE_URL="sqlite+aiosqlite:///./ciso_digital.db"
```

Or configure in `backend/.env`:

```ini
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ciso_digital
```

### 3. Verify Setup

```bash
cd backend
alembic current
```

You should see:
```
INFO  [alembic.runtime.migration] Context impl PostgreSQLImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

---

## Common Commands

### Check Current Migration Version

```bash
alembic current
```

Shows which migration version the database is currently at.

### View Migration History

```bash
alembic history
```

Shows all available migrations with their revision IDs.

```bash
alembic history --verbose
```

Shows detailed migration information.

### Upgrade Database

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade by one version
alembic upgrade +1

# Upgrade to specific revision
alembic upgrade 4858716f5228
```

### Downgrade Database

```bash
# Downgrade by one version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade 4858716f5228

# Downgrade to base (empty database)
alembic downgrade base
```

⚠️ **WARNING:** Downgrading can cause **data loss**. Always backup production data first!

### Show SQL Without Executing

```bash
# See SQL that would be executed (offline mode)
alembic upgrade head --sql

# Save SQL to file
alembic upgrade head --sql > migration.sql
```

Useful for reviewing changes before applying them in production.

---

## Creating New Migrations

### Automatic Migration (Recommended)

Alembic can auto-detect changes to your SQLAlchemy models:

```bash
# 1. Modify your models in app/shared/models/
# For example, add a new column to Risk model

# 2. Generate migration
alembic revision --autogenerate -m "add risk_priority_field"
```

This creates a new migration file in `alembic/versions/` like:
```
xxxxxxxxxxxx_add_risk_priority_field.py
```

#### 3. Review the Generated Migration

**IMPORTANT:** Always review auto-generated migrations! Alembic may miss:
- Renamed columns (appears as drop + add)
- Data migrations
- Custom constraints
- Certain PostgreSQL-specific features

```python
# alembic/versions/xxxxxxxxxxxx_add_risk_priority_field.py

def upgrade() -> None:
    """Add priority field to risks table."""
    op.add_column(
        "risks",
        sa.Column("priority", sa.Integer(), nullable=True)
    )

def downgrade() -> None:
    """Remove priority field from risks table."""
    op.drop_column("risks", "priority")
```

#### 4. Test the Migration

```bash
# Test upgrade
alembic upgrade head

# Verify changes
alembic current

# Test downgrade (optional, careful in production!)
alembic downgrade -1
alembic upgrade head
```

### Manual Migration

For complex changes (data migrations, custom logic), create an empty migration:

```bash
alembic revision -m "migrate_risk_severity_values"
```

Then edit the generated file:

```python
"""migrate_risk_severity_values

Revision ID: xxxxxxxxxxxx
Revises: previous_revision_id
Create Date: 2026-02-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    """
    Migrate old severity values to new severity scale.
    
    Old: 1-5 numeric scale
    New: critical/high/medium/low enum
    """
    # Step 1: Add new column
    op.add_column(
        "risks",
        sa.Column("severity_new", sa.String(20), nullable=True)
    )
    
    # Step 2: Migrate data
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE risks
            SET severity_new = CASE
                WHEN severity_old = 5 THEN 'critical'
                WHEN severity_old = 4 THEN 'high'
                WHEN severity_old = 3 THEN 'medium'
                ELSE 'low'
            END
        """)
    )
    
    # Step 3: Drop old column, rename new column
    op.drop_column("risks", "severity_old")
    op.alter_column("risks", "severity_new", new_column_name="severity")
    
    # Step 4: Make column non-nullable
    op.alter_column("risks", "severity", nullable=False)


def downgrade() -> None:
    """Reverse the severity migration."""
    # Implement reverse logic here
    # WARNING: May lose data if new values don't map cleanly to old format
    pass
```

---

## Testing Migrations

### Automated Test Script

We provide a test script that validates migrations using SQLite:

```bash
cd backend
python scripts/test_migrations.py
```

This script:
1. Creates a test SQLite database
2. Runs `alembic upgrade head`
3. Verifies table structure
4. Runs `alembic downgrade base`
5. Verifies cleanup

**Expected output:**

```
======================================================================
Testing Alembic Migrations with SQLite
======================================================================

[UPGRADE] Running migration: alembic upgrade head
[SUCCESS] Upgrade successful

[VERIFY] Verifying tables were created...
   Tables found: ['alembic_version', 'risks']
[SUCCESS] All expected tables exist

...

======================================================================
[SUCCESS] ALL MIGRATION TESTS PASSED!
======================================================================
```

### Manual Testing

#### 1. Test on Local SQLite

```bash
# Use SQLite for quick local testing
export DATABASE_URL="sqlite:///./test_migration.db"

# Run migration
alembic upgrade head

# Inspect database
sqlite3 test_migration.db
.tables
.schema risks
.quit
```

#### 2. Test on Local PostgreSQL

```bash
# Start PostgreSQL (Docker)
docker run -d -p 5432:5432 \
  -e POSTGRES_DB=ciso_test \
  -e POSTGRES_PASSWORD=testpass \
  postgres:16

# Set DATABASE_URL
export DATABASE_URL="postgresql+asyncpg://postgres:testpass@localhost:5432/ciso_test"

# Run migration
alembic upgrade head

# Verify
psql postgresql://postgres:testpass@localhost:5432/ciso_test
\dt
\d risks
\q
```

#### 3. Test in CI/CD

Add to your GitHub Actions or CI pipeline:

```yaml
# .github/workflows/test.yml

jobs:
  test-migrations:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: ciso_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Test migrations (SQLite)
        run: |
          cd backend
          python scripts/test_migrations.py
      
      - name: Test migrations (PostgreSQL)
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:testpass@localhost:5432/ciso_test
        run: |
          cd backend
          alembic upgrade head
          alembic downgrade base
```

---

## Best Practices

### 1. Always Review Auto-Generated Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# REVIEW the generated file in alembic/versions/
# Check for:
# - Unintended changes
# - Missing changes
# - Correct column types
# - Proper constraints
```

### 2. Write Reversible Migrations

Every `upgrade()` should have a corresponding `downgrade()`:

```python
# ✅ GOOD - Reversible
def upgrade():
    op.add_column("risks", sa.Column("priority", sa.Integer()))

def downgrade():
    op.drop_column("risks", "priority")


# ❌ BAD - Not reversible
def upgrade():
    op.add_column("risks", sa.Column("priority", sa.Integer()))

def downgrade():
    pass  # ❌ Can't rollback!
```

### 3. Handle Data Migrations Carefully

When modifying data, consider:

```python
def upgrade():
    # Add new column with default
    op.add_column(
        "risks",
        sa.Column("severity_score", sa.Float(), server_default="0.0")
    )
    
    # Populate data
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE risks
            SET severity_score = CASE
                WHEN severity = 'critical' THEN 10.0
                WHEN severity = 'high' THEN 7.5
                WHEN severity = 'medium' THEN 5.0
                ELSE 2.5
            END
        """)
    )
    
    # Remove default after data population
    op.alter_column("risks", "severity_score", server_default=None)
```

### 4. Test Before Production

```bash
# 1. Test on local database
alembic upgrade head

# 2. Verify application works
pytest tests/

# 3. Test downgrade (if safe)
alembic downgrade -1
alembic upgrade head

# 4. Run in staging environment
# 5. Only then deploy to production
```

### 5. Backup Production Before Migration

```bash
# PostgreSQL backup
pg_dump -U user -d ciso_digital -F c -f backup_before_migration.dump

# Restore if needed
pg_restore -U user -d ciso_digital backup_before_migration.dump
```

### 6. Use Descriptive Migration Messages

```bash
# ✅ GOOD
alembic revision -m "add_priority_and_tags_to_risks_table"
alembic revision -m "migrate_severity_from_numeric_to_enum"

# ❌ BAD
alembic revision -m "update"
alembic revision -m "fix"
alembic revision -m "changes"
```

### 7. Make Enum Changes PostgreSQL-Aware

```python
def upgrade():
    bind = op.get_bind()
    
    if bind.dialect.name == "postgresql":
        # PostgreSQL needs special handling for enums
        op.execute("ALTER TYPE riskseverity ADD VALUE 'critical'")
    else:
        # SQLite uses VARCHAR, no special handling needed
        pass

def downgrade():
    bind = op.get_bind()
    
    if bind.dialect.name == "postgresql":
        # PostgreSQL can't remove enum values easily
        # May need to recreate the enum type
        pass
```

### 8. Avoid Blocking Operations in Production

```python
# ❌ BAD - Locks table during migration
op.add_column("risks", sa.Column("priority", sa.Integer(), nullable=False))

# ✅ GOOD - Add as nullable first, populate, then make non-nullable
def upgrade():
    # Step 1: Add as nullable
    op.add_column("risks", sa.Column("priority", sa.Integer(), nullable=True))
    
    # Step 2: Populate with default
    op.execute("UPDATE risks SET priority = 3 WHERE priority IS NULL")
    
    # Step 3: Make non-nullable
    op.alter_column("risks", "priority", nullable=False)
```

---

## Troubleshooting

### Error: "Target database is not up to date"

**Cause:** Someone else applied a migration you don't have locally.

**Solution:**
```bash
git pull origin main
alembic upgrade head
```

### Error: "Can't locate revision identified by 'xxxx'"

**Cause:** Migration file deleted or branch mismatch.

**Solution:**
```bash
# Check current version
alembic current

# View history
alembic history

# If database is ahead, stamp to a known version
alembic stamp head
```

### Error: "sqlalchemy.exc.ProgrammingError: relation already exists"

**Cause:** Trying to create a table that already exists.

**Solution:**
```bash
# Check current state
alembic current

# Stamp database to match actual state (CAREFUL!)
alembic stamp head
```

### Error: "asyncio extension requires an async driver"

**Cause:** Using `sqlite:///` instead of `sqlite+aiosqlite:///`.

**Solution:**
```bash
# Use async driver
export DATABASE_URL="sqlite+aiosqlite:///./ciso_digital.db"
```

### Async/Sync Issues

Our `env.py` automatically handles this:
- **SQLite** → Runs synchronous migrations
- **PostgreSQL** → Runs async migrations

If you encounter issues, check `alembic/env.py` line 115+.

### Multiple Heads

**Cause:** Parallel branches created migrations independently.

**Solution:**
```bash
# Create a merge migration
alembic merge heads -m "merge_migrations"
alembic upgrade head
```

---

## Configuration Files

### `alembic.ini`

Main configuration file. Key settings:

```ini
[alembic]
# Script location
script_location = alembic

# Version locations (where migrations are stored)
version_locations = alembic/versions

# File template
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

# Post-write hooks (auto-format with black)
post_write_hooks = black
```

### `alembic/env.py`

Environment configuration. Key features:

- **Imports models**: `from app.shared.models import Base`
- **Dynamic DATABASE_URL**: Uses `app.core.config.settings.DATABASE_URL`
- **Async support**: Uses `async_engine_from_config` for PostgreSQL
- **SQLite compatibility**: Falls back to sync engine for SQLite
- **Compare options**: `compare_type=True`, `compare_server_default=True`

---

## Migration File Structure

```python
"""descriptive_message_here

Revision ID: 4858716f5228
Revises: 
Create Date: 2026-02-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '4858716f5228'
down_revision = None  # First migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Apply migration changes.
    
    This function runs when `alembic upgrade` is executed.
    """
    # Migration logic here
    op.create_table(...)


def downgrade() -> None:
    """
    Revert migration changes.
    
    This function runs when `alembic downgrade` is executed.
    """
    # Reverse migration logic here
    op.drop_table(...)
```

---

## CI/CD Integration

### Pre-deployment Checklist

Before deploying to production:

1. ✅ All migrations tested locally
2. ✅ Migrations tested in staging
3. ✅ Database backed up
4. ✅ Downgrade strategy prepared
5. ✅ Monitoring set up for migration execution time
6. ✅ Rollback plan documented

### Deployment Script Example

```bash
#!/bin/bash
# deploy.sh

set -e  # Exit on error

echo "🔄 Starting deployment..."

# 1. Backup database
echo "📦 Creating backup..."
pg_dump -U $DB_USER -d $DB_NAME -F c -f "backup_$(date +%Y%m%d_%H%M%S).dump"

# 2. Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# 3. Restart application
echo "🚀 Restarting application..."
systemctl restart ciso-digital

# 4. Verify
echo "✅ Verifying deployment..."
curl -f http://localhost:8000/health || {
    echo "❌ Health check failed! Rolling back..."
    alembic downgrade -1
    systemctl restart ciso-digital
    exit 1
}

echo "✅ Deployment successful!"
```

---

## Additional Resources

- **Alembic Documentation**: https://alembic.sqlalchemy.org/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Our Development Standards**: `../docs/09-DEVELOPMENT-STANDARDS.md`
- **Project Architecture**: `../docs/01-TECHNICAL-ARCHITECTURE.md`

---

## Support

For issues or questions:

1. Check this documentation
2. Review existing migrations in `versions/`
3. Check `alembic/env.py` configuration
4. Ask the development team

**Last Updated:** February 2026  
**Maintained by:** Backend Team
