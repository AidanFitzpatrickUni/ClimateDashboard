"""
Tests for the data loading utilities.
"""

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.database]
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Make sure we can import from the backend
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR.parent))

from backend.utils.data_loader import (
    load_main,
    load_co2,
    load_sea_level,
    merge_datasets,
    merge_with_sea_level,
    split_data,
    save_predictions,
    set_db_path,
    _read_table
)


class TestDataLoader:
    """Check that we can load data from the database properly."""
    
    def test_load_main(self, temp_db):
        """Make sure we can pull temperature data from the database."""
        set_db_path(temp_db)
        df = load_main()
        
        assert isinstance(df, pd.DataFrame)
        assert 'year' in df.columns
        assert 'anthropogenic_c' in df.columns
        assert 'observed_c' in df.columns
        assert len(df) > 0
        assert df['year'].min() >= 1850
    
    def test_load_co2(self, temp_db):
        """Check that CO2 data loads correctly."""
        set_db_path(temp_db)
        df = load_co2()
        
        assert isinstance(df, pd.DataFrame)
        assert 'year' in df.columns
        assert 'co2_ppm' in df.columns
        assert len(df) > 0
    
    def test_load_sea_level(self, temp_db):
        """Verify sea level measurements load properly."""
        set_db_path(temp_db)
        df = load_sea_level()
        
        assert isinstance(df, pd.DataFrame)
        assert 'year' in df.columns
        assert 'gmsl' in df.columns
        assert len(df) > 0
    
    def test_merge_datasets(self, temp_db):
        """Make sure we can combine temperature and CO2 data together."""
        set_db_path(temp_db)
        main_df = load_main()
        co2_df = load_co2()
        
        merged = merge_datasets(main_df, co2_df)
        
        assert isinstance(merged, pd.DataFrame)
        assert 'co2_ppm' in merged.columns
        assert 'ln_co2_ratio' in merged.columns
        assert len(merged) == len(main_df)
        assert not merged['ln_co2_ratio'].isna().all()
    
    def test_merge_with_sea_level(self, temp_db):
        """Check that we can merge temperature and sea level data."""
        set_db_path(temp_db)
        main_df = load_main()
        sea_df = load_sea_level()
        
        # Need to merge temp data first before adding sea level
        co2_df = load_co2()
        temp_data = merge_datasets(main_df, co2_df)
        
        merged = merge_with_sea_level(temp_data, sea_df)
        
        assert isinstance(merged, pd.DataFrame)
        assert 'gmsl' in merged.columns
        assert 'observed_c' in merged.columns
    
    def test_split_data(self, sample_temperature_data):
        """Verify the data gets split into train/validation/test correctly."""
        train, val, test = split_data(sample_temperature_data)
        
        assert len(train) > 0
        assert len(val) > 0
        assert len(test) > 0
        assert train['year'].max() <= 2005
        assert val['year'].min() >= 2006
        assert val['year'].max() <= 2015
        assert test['year'].min() >= 2016
        assert len(train) + len(val) + len(test) == len(sample_temperature_data)
    
    def test_save_predictions(self, temp_db):
        """Make sure predictions get saved to the database properly."""
        set_db_path(temp_db)
        years = np.arange(2025, 2051)
        predictions = np.random.randn(len(years)) * 0.5 + 1.5
        
        save_predictions(years, predictions, table_name="test_predictions")
        
        # Check that it actually saved
        df = _read_table("test_predictions")
        assert len(df) == len(years)
        assert 'year' in df.columns
        assert 'prediction' in df.columns
        assert df['year'].min() == 2025
        assert df['year'].max() == 2050

