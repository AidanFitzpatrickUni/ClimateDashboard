"""
Tests for the sea level prediction model.
"""

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.model]
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Set up imports
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR.parent))

from backend.model.sea_level_model import (
    train_sea_poly_model,
    train_sea_xgb_residual,
    predict_sea_future,
    _make_features
)


class TestSeaLevelModel:
    """Check that the sea level model works properly."""
    
    def test_train_sea_poly_model(self, sample_sea_level_data):
        """Make sure the sea level polynomial model can train."""
        train, _, _ = self._split_data(sample_sea_level_data)
        
        model = train_sea_poly_model(train)
        
        assert model is not None
        assert hasattr(model, 'predict')
        
        # Try making predictions
        predictions = model.predict(train[['year']])
        assert len(predictions) == len(train)
        assert not np.isnan(predictions).any()
    
    def test_train_sea_xgb_residual(self, sample_sea_level_data):
        """Verify the sea level XGBoost residual model trains correctly."""
        train, _, _ = self._split_data(sample_sea_level_data)
        poly = train_sea_poly_model(train)
        
        xgb = train_sea_xgb_residual(train, poly)
        
        assert xgb is not None
        assert hasattr(xgb, 'predict')
        assert hasattr(xgb, 'feature_importances_')
    
    def test_make_features(self, sample_sea_level_data):
        """Check that sea level features are created properly."""
        features = _make_features(sample_sea_level_data)
        
        assert isinstance(features, pd.DataFrame)
        assert 'year_c' in features.columns
        assert 'year_c2' in features.columns
        assert 'temp' in features.columns
        assert 'temp2' in features.columns
        assert len(features) == len(sample_sea_level_data)
    
    def test_predict_sea_future(self, sample_sea_level_data):
        """Make sure we can generate future sea level predictions."""
        train, _, _ = self._split_data(sample_sea_level_data)
        poly = train_sea_poly_model(train)
        xgb = train_sea_xgb_residual(train, poly)
        
        # Use some fake temperature predictions for testing
        future_years = np.arange(2025, 2051)
        future_temps = np.linspace(1.5, 2.0, len(future_years))
        
        years, poly_pred, hybrid_pred, anchored = predict_sea_future(
            poly, xgb, sample_sea_level_data, future_years, future_temps
        )
        
        assert len(years) == 26
        assert len(poly_pred) == 26
        assert len(hybrid_pred) == 26
        assert len(anchored) == 26
        assert years[0] == 2025
        assert years[-1] == 2050
        assert not np.isnan(anchored).any()
    
    def _split_data(self, df):
        """Helper function to split data into train/val/test."""
        train = df[df["year"] <= 2005].copy()
        val = df[(df["year"] >= 2006) & (df["year"] <= 2015)].copy()
        test = df[df["year"] >= 2016].copy()
        return train, val, test

