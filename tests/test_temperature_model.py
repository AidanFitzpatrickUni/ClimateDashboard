"""
Tests for the temperature prediction model.
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

from backend.model.temprature_model import (
    train_poly_model,
    train_xgb_residual,
    poly_equation,
    predict_future,
    _make_features,
    _calculate_metrics
)


class TestTemperatureModel:
    """Check that the temperature model works as expected."""
    
    def test_train_poly_model(self, sample_temperature_data):
        """Make sure the polynomial model can train without errors."""
        train, _, _ = self._split_data(sample_temperature_data)
        
        model = train_poly_model(train, degree=2)
        
        assert model is not None
        assert hasattr(model, 'predict')
        
        # Try making some predictions
        predictions = model.predict(train[['year']])
        assert len(predictions) == len(train)
        assert not np.isnan(predictions).any()
    
    def test_poly_equation(self, sample_temperature_data):
        """Check that we can extract the polynomial equation as a string."""
        train, _, _ = self._split_data(sample_temperature_data)
        model = train_poly_model(train, degree=2)
        
        equation = poly_equation(model)
        
        assert isinstance(equation, str)
        assert 'y =' in equation
        assert 'x^' in equation
    
    def test_make_features(self, sample_temperature_data):
        """Verify that feature engineering creates the right columns."""
        features = _make_features(sample_temperature_data)
        
        assert isinstance(features, pd.DataFrame)
        assert 'year_c' in features.columns
        assert 'year_c2' in features.columns
        assert 'anthro_c' in features.columns
        assert 'anthro_f' in features.columns
        assert 'co2_ppm' in features.columns
        assert 'ln_co2_ratio' in features.columns
        assert len(features) == len(sample_temperature_data)
    
    def test_train_xgb_residual(self, sample_temperature_data):
        """Make sure the XGBoost residual model trains correctly."""
        train, _, _ = self._split_data(sample_temperature_data)
        poly = train_poly_model(train, degree=2)
        
        xgb = train_xgb_residual(train, poly)
        
        assert xgb is not None
        assert hasattr(xgb, 'predict')
        assert hasattr(xgb, 'feature_importances_')
        assert len(xgb.feature_importances_) == 6
    
    def test_predict_future(self, sample_temperature_data):
        """Check that we can generate future temperature predictions."""
        train, _, _ = self._split_data(sample_temperature_data)
        poly = train_poly_model(train, degree=2)
        xgb = train_xgb_residual(train, poly)
        
        years, co2_future, poly_pred, hybrid_pred, anchored = predict_future(
            poly, xgb, sample_temperature_data, start=2025, end=2050
        )
        
        assert len(years) == 26  # Should cover 2025 to 2050
        assert len(co2_future) == 26
        assert len(poly_pred) == 26
        assert len(hybrid_pred) == 26
        assert len(anchored) == 26
        assert years[0] == 2025
        assert years[-1] == 2050
        assert not np.isnan(anchored).any()
    
    def test_calculate_metrics(self):
        """Verify that evaluation metrics are calculated correctly."""
        y_true = np.array([1.0, 1.5, 2.0, 2.5, 3.0])
        y_pred = np.array([1.1, 1.4, 2.1, 2.4, 3.1])
        
        mse, rmse, mae, r2, resids = _calculate_metrics(y_true, y_pred)
        
        assert mse > 0
        assert rmse > 0
        assert mae > 0
        assert isinstance(r2, float)
        assert len(resids) == len(y_true)
    
    def _split_data(self, df):
        """Helper function to split the data into train/val/test."""
        train = df[df["year"] <= 2005].copy()
        val = df[(df["year"] >= 2006) & (df["year"] <= 2015)].copy()
        test = df[df["year"] >= 2016].copy()
        return train, val, test

