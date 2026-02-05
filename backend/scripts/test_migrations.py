#!/usr/bin/env python3
"""
Test migration script using SQLite.

This script tests migrations in isolation using a SQLite database.
Useful for CI/CD pipelines and local development without PostgreSQL.

Usage:
    python scripts/test_migrations.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set test database URL before importing settings
os.environ["DATABASE_URL"] = "sqlite:///./test_migrations.db"

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text


def test_migrations():
    """
    Test migrations by running upgrade and downgrade.
    
    Steps:
    1. Delete test database if exists
    2. Run alembic upgrade head
    3. Verify tables were created
    4. Run alembic downgrade base
    5. Verify tables were dropped
    """
    print("=" * 70)
    print("Testing Alembic Migrations with SQLite")
    print("=" * 70)
    
    # Path to test database
    test_db_path = backend_dir / "test_migrations.db"
    
    # Clean up old test database
    if test_db_path.exists():
        print(f"\n[CLEANUP] Removing old test database: {test_db_path}")
        test_db_path.unlink()
    
    # Configure Alembic
    alembic_cfg = Config(backend_dir / "alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{test_db_path}")
    
    print("\n[UPGRADE] Running migration: alembic upgrade head")
    try:
        command.upgrade(alembic_cfg, "head")
        print("[SUCCESS] Upgrade successful")
    except Exception as e:
        print(f"[FAILED] Upgrade failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Verify tables were created
    print("\n[VERIFY] Verifying tables were created...")
    engine = create_engine(f"sqlite:///{test_db_path}")
    
    with engine.connect() as conn:
        # Get table names
        inspector = inspect(conn)
        tables = inspector.get_table_names()
        
        print(f"   Tables found: {tables}")
        
        if "risks" not in tables:
            print("[FAILED] 'risks' table not found!")
            return False
        
        if "alembic_version" not in tables:
            print("[FAILED] 'alembic_version' table not found!")
            return False
        
        print("[SUCCESS] All expected tables exist")
        
        # Verify risks table structure
        print("\n[VERIFY] Verifying risks table columns...")
        columns = [col["name"] for col in inspector.get_columns("risks")]
        
        expected_columns = [
            "id",
            "risk_number",
            "title",
            "description",
            "severity",
            "likelihood",
            "category",
            "impact_score",
            "status",
            "assigned_to",
            "mitigation_plan",
            "deadline",
            "created_at",
            "updated_at",
        ]
        
        print(f"   Columns found: {len(columns)}")
        print(f"   Expected: {len(expected_columns)}")
        
        for col in expected_columns:
            if col not in columns:
                print(f"[FAILED] Missing column: {col}")
                return False
        
        print("[SUCCESS] All expected columns exist")
        print(f"   Columns: {', '.join(columns)}")
        
        # Check migration version
        print("\n[VERIFY] Checking migration version...")
        version_result = conn.execute(text("SELECT version_num FROM alembic_version"))
        version = version_result.scalar_one()
        print(f"   Current version: {version}")
        print("[SUCCESS] Version table populated")
        
        # Check indexes
        print("\n[VERIFY] Checking indexes...")
        indexes = inspector.get_indexes("risks")
        print(f"   Indexes found: {len(indexes)}")
        for idx in indexes:
            print(f"      - {idx['name']}: {idx['column_names']}")
        print("[SUCCESS] Indexes created")
    
    engine.dispose()
    
    # Test downgrade
    print("\n[DOWNGRADE] Running migration: alembic downgrade base")
    try:
        command.downgrade(alembic_cfg, "base")
        print("[SUCCESS] Downgrade successful")
    except Exception as e:
        print(f"[FAILED] Downgrade failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Verify tables were dropped
    print("\n[VERIFY] Verifying tables were dropped...")
    engine = create_engine(f"sqlite:///{test_db_path}")
    
    with engine.connect() as conn:
        inspector = inspect(conn)
        tables = inspector.get_table_names()
        
        print(f"   Tables remaining: {tables}")
        
        if "risks" in tables:
            print("[FAILED] 'risks' table still exists after downgrade!")
            return False
        
        print("[SUCCESS] Tables properly cleaned up")
    
    engine.dispose()
    
    # Clean up test database
    print(f"\n[CLEANUP] Cleaning up test database: {test_db_path}")
    if test_db_path.exists():
        test_db_path.unlink()
    
    print("\n" + "=" * 70)
    print("[SUCCESS] ALL MIGRATION TESTS PASSED!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = test_migrations()
    sys.exit(0 if success else 1)
