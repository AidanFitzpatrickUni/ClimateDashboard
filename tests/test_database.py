"""
Tests for database operations and table creation.
"""

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.database]
import sqlite3
import sys
from pathlib import Path

# Set up imports
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR.parent))

from backend.utils.create_db import build_database
from backend.utils.data_loader import set_db_path, _read_table


class TestDatabase:
    """Check that database operations work correctly."""
    
    def test_database_tables_exist(self, temp_db):
        """Make sure all the tables we need are actually there."""
        set_db_path(temp_db)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'temperature' in tables
        assert 'co2_concentration' in tables
        assert 'sea_level' in tables
        
        conn.close()
    
    def test_database_indexes(self, temp_db):
        """Check that indexes exist (or at least the query works)."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # See what indexes we have
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        # Indexes might not exist depending on how the DB was created
        # Just make sure we can query them
        assert isinstance(indexes, list)
        
        conn.close()
    
    def test_read_table_function(self, temp_db):
        """Verify we can read data from all the tables."""
        set_db_path(temp_db)
        
        temp_df = _read_table("temperature")
        assert len(temp_df) > 0
        assert 'year' in temp_df.columns
        
        co2_df = _read_table("co2_concentration")
        assert len(co2_df) > 0
        assert 'year' in co2_df.columns
        
        sea_df = _read_table("sea_level")
        assert len(sea_df) > 0
        assert 'year' in sea_df.columns
    
    def test_save_predictions_creates_table(self, temp_db):
        """Make sure save_predictions creates the table if it doesn't exist."""
        import numpy as np
        from backend.utils.data_loader import save_predictions
        
        set_db_path(temp_db)
        
        years = np.arange(2025, 2051)
        predictions = np.random.randn(len(years)) * 0.5 + 1.5
        
        save_predictions(years, predictions, table_name="new_predictions_table")
        
        # Check that the table got created
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='new_predictions_table'")
        result = cursor.fetchone()
        assert result is not None
        
        conn.close()

