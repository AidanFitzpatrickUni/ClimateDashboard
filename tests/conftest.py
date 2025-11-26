"""
Shared test fixtures and configuration for all tests.
"""

import pytest
import sqlite3
import tempfile
import shutil
import time
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Find the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"


@pytest.fixture
def temp_db():
    """Create a temporary database with sample data for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_climate.db"
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Set up tables with some fake data
    cursor.execute("""
        CREATE TABLE temperature (
            year INTEGER PRIMARY KEY,
            anthropogenic_c REAL,
            observed_c REAL,
            anthropogenic_f REAL
        )
    """)
    
    # Add some fake temperature data
    for year in range(1850, 2025):
        cursor.execute(
            "INSERT INTO temperature (year, anthropogenic_c, observed_c, anthropogenic_f) VALUES (?, ?, ?, ?)",
            (year, 0.5, 0.3, 0.4)
        )
    
    cursor.execute("""
        CREATE TABLE co2_concentration (
            year INTEGER PRIMARY KEY,
            co2_ppm REAL
        )
    """)
    
    # Add fake CO2 data
    for year in range(1850, 2025):
        cursor.execute(
            "INSERT INTO co2_concentration (year, co2_ppm) VALUES (?, ?)",
            (year, 280 + (year - 1850) * 0.5)
        )
    
    cursor.execute("""
        CREATE TABLE sea_level (
            year INTEGER PRIMARY KEY,
            gmsl REAL
        )
    """)
    
    # Add fake sea level data
    for year in range(1901, 2025):
        cursor.execute(
            "INSERT INTO sea_level (year, gmsl) VALUES (?, ?)",
            (year, (year - 1901) * 0.5)
        )
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Clean up the temp directory
    # Windows sometimes holds file locks, so we need to wait a bit
    if sys.platform == 'win32':
        time.sleep(0.1)  # Give Windows time to release file handles
    
    try:
        shutil.rmtree(temp_dir)
    except PermissionError:
        # Sometimes files are still locked on Windows, try again
        time.sleep(0.2)
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass  # If it still fails, the OS will clean it up eventually


@pytest.fixture
def sample_temperature_data():
    """Create some fake temperature data for testing."""
    years = np.arange(1850, 2025)
    return pd.DataFrame({
        'year': years,
        'anthropogenic_c': np.random.randn(len(years)) * 0.1 + 0.5,
        'observed_c': np.random.randn(len(years)) * 0.1 + 0.3,
        'anthropogenic_f': np.random.randn(len(years)) * 0.1 + 0.4,
        'co2_ppm': 280 + (years - 1850) * 0.5,
        'ln_co2_ratio': np.log((280 + (years - 1850) * 0.5) / 278.0)
    })


@pytest.fixture
def sample_sea_level_data():
    """Create some fake sea level data for testing."""
    years = np.arange(1901, 2025)
    return pd.DataFrame({
        'year': years,
        'gmsl': (years - 1901) * 0.5 + np.random.randn(len(years)) * 0.1,
        'observed_c': np.random.randn(len(years)) * 0.1 + 0.3
    })


@pytest.fixture
def app_client():
    """Set up a Flask test client so we can test the API."""
    import sys
    sys.path.insert(0, str(BACKEND_DIR.parent))
    
    from backend.app import app
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client

