"""
Model utilities for projecting global mean sea level using temperature-driven
features and a hybrid polynomial + XGBoost stack.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from xgboost import XGBRegressor

_REF_YEAR = 2000  # Maintain feature centering parity with temperature model


def train_sea_poly_model(train_df: pd.DataFrame, degree: int = 2, alpha: float = 0.1):
    """
    Baseline polynomial that captures the long-term sea level trend vs. year.
    """
    X = train_df[["year"]]
    y = train_df["gmsl"].astype(float)

    model = make_pipeline(
        PolynomialFeatures(degree=degree, include_bias=False),
        Ridge(alpha=alpha),
    )

    # Emphasize recent acceleration to better match current trajectory
    weights = np.where(train_df["year"] >= 1990, 3.0, 1.0)
    model.fit(X, y, ridge__sample_weight=weights)
    return model


def _make_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assemble engineered residual features using year and temperature context.
    """
    out = pd.DataFrame(index=df.index)
    yr = df["year"].astype(float)
    temp = df["observed_c"].astype(float)

    out["year_c"] = yr - _REF_YEAR
    out["year_c2"] = out["year_c"] ** 2
    out["temp"] = temp
    out["temp2"] = temp**2
    return out


def train_sea_xgb_residual(train_df: pd.DataFrame, poly_model):
    """
    Residual learner that leverages temperature features to refine predictions.
    """
    baseline = poly_model.predict(train_df[["year"]])
    residuals = train_df["gmsl"].values - baseline

    X = _make_features(train_df)
    # Slightly shallower trees avoid overfitting to short temperature swings
    model = XGBRegressor(
        n_estimators=1500,
        learning_rate=0.02,
        max_depth=4,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        tree_method="hist",
        random_state=42,
    )
    model.fit(X, residuals, verbose=False)
    return model


def predict_sea_future(
    poly_model,
    xgb_model,
    historical_df: pd.DataFrame,
    future_years,
    future_temps,
):
    """
    Generate anchored sea-level forecasts using projected temperatures.
    """
    years = np.array(future_years)
    years_df = pd.DataFrame({"year": years})
    poly_pred = poly_model.predict(years_df)

    future_df = pd.DataFrame(
        {
            "year": years,
            "observed_c": future_temps,
        }
    )

    resid_pred = xgb_model.predict(_make_features(future_df))
    hybrid = poly_pred + resid_pred

    last_obs = historical_df.iloc[-1]["gmsl"]
    last_year = historical_df.iloc[-1]["year"]
    last_temp = historical_df.iloc[-1]["observed_c"]

    last_poly = poly_model.predict(pd.DataFrame({"year": [last_year]}))[0]
    last_resid = xgb_model.predict(
        _make_features(pd.DataFrame({"year": [last_year], "observed_c": [last_temp]}))
    )[0]
    offset = last_obs - (last_poly + last_resid)
    anchored = hybrid + offset

    return years, poly_pred, hybrid, anchored

