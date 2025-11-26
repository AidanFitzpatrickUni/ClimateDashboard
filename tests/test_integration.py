"""
Integration tests that run the full pipeline end-to-end.
"""

import pytest

pytestmark = [pytest.mark.integration]
import sys
import numpy as np
from pathlib import Path

# Set up imports
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
    set_db_path
)
from backend.model.temprature_model import (
    train_poly_model,
    train_xgb_residual,
    predict_future
)
from backend.model.sea_level_model import (
    train_sea_poly_model,
    train_sea_xgb_residual,
    predict_sea_future
)


class TestIntegration:
    """Run the complete pipeline from start to finish."""
    
    def test_full_temperature_pipeline(self, temp_db):
        """Run the whole temperature prediction pipeline and make sure it works."""
        set_db_path(temp_db)
        
        # Load up the data
        main_df = load_main()
        co2_df = load_co2()
        data = merge_datasets(main_df, co2_df)
        
        assert len(data) > 0
        assert 'co2_ppm' in data.columns
        
        # Split into train/val/test
        train, val, test = split_data(data)
        
        assert len(train) > 0
        assert len(val) > 0
        assert len(test) > 0
        
        # Train both models
        poly = train_poly_model(train, degree=2)
        xgb = train_xgb_residual(train, poly)
        
        assert poly is not None
        assert xgb is not None
        
        # Generate future predictions
        years, co2_future, poly_pred, hybrid_pred, anchored = predict_future(
            poly, xgb, data, start=2025, end=2050
        )
        
        assert len(years) == 26
        assert len(anchored) == 26
        assert not np.isnan(anchored).any()
        
        # Save them to the database
        save_predictions(years, anchored, table_name="test_temp_predictions")
        
        # Make sure they actually got saved
        from backend.utils.data_loader import _read_table
        saved = _read_table("test_temp_predictions")
        assert len(saved) == 26
    
    def test_full_sea_level_pipeline(self, temp_db):
        """Run the complete sea level prediction pipeline."""
        set_db_path(temp_db)
        
        # Load all the data we need
        main_df = load_main()
        co2_df = load_co2()
        sea_df = load_sea_level()
        
        temp_data = merge_datasets(main_df, co2_df)
        sea_dataset = merge_with_sea_level(temp_data, sea_df)
        
        assert len(sea_dataset) > 0
        assert 'gmsl' in sea_dataset.columns
        
        # Split the data
        train, val, test = split_data(sea_dataset)
        
        # Train the models
        sea_poly = train_sea_poly_model(train)
        sea_xgb = train_sea_xgb_residual(train, sea_poly)
        
        # Use some fake temperature predictions for testing
        future_years = np.arange(2025, 2051)
        future_temps = np.linspace(1.5, 2.0, len(future_years))
        
        # Generate predictions
        years, poly_pred, hybrid_pred, anchored = predict_sea_future(
            sea_poly, sea_xgb, sea_dataset, future_years, future_temps
        )
        
        assert len(years) == 26
        assert len(anchored) == 26
        assert not np.isnan(anchored).any()
        
        # Save to database
        save_predictions(years, anchored, table_name="test_sea_predictions")
        
        # Check that it saved
        from backend.utils.data_loader import _read_table
        saved = _read_table("test_sea_predictions")
        assert len(saved) == 26
    
    def test_end_to_end_pipeline(self, temp_db):
        """Run everything from loading data to saving predictions for both models."""
        set_db_path(temp_db)
        
        # Do the temperature pipeline first
        main_df = load_main()
        co2_df = load_co2()
        data = merge_datasets(main_df, co2_df)
        train, _, _ = split_data(data)
        
        poly = train_poly_model(train, degree=2)
        xgb = train_xgb_residual(train, poly)
        years, _, _, _, anchored = predict_future(poly, xgb, data, start=2025, end=2050)
        save_predictions(years, anchored, table_name="future_predictions")
        
        # Then do sea level using the temperature predictions
        sea_df = load_sea_level()
        sea_dataset = merge_with_sea_level(data, sea_df)
        sea_train, _, _ = split_data(sea_dataset)
        
        sea_poly = train_sea_poly_model(sea_train)
        sea_xgb = train_sea_xgb_residual(sea_train, sea_poly)
        sea_years, _, _, sea_anchored = predict_sea_future(
            sea_poly, sea_xgb, sea_dataset, years, anchored
        )
        save_predictions(sea_years, sea_anchored, table_name="sea_level_predictions")
        
        # Make sure both got saved properly
        from backend.utils.data_loader import _read_table
        temp_preds = _read_table("future_predictions")
        sea_preds = _read_table("sea_level_predictions")
        
        assert len(temp_preds) == 26
        assert len(sea_preds) == 26

