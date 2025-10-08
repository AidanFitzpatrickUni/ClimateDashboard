"""
Model training, evaluation, and future projection utilities
for the Climate Change Prediction project.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from xgboost import XGBRegressor

_REF_YEAR = 2000  # Reference year for centering features

def train_poly_model(train_data: pd.DataFrame, degree: int = 2, alpha: float = 0.1):
    """
    Train a polynomial regression model mapping year → observed warming.
    """
    X = train_data[["year"]]
    y = train_data["observed_c"].astype(float)

    model = make_pipeline(
        PolynomialFeatures(degree=degree, include_bias=False),
        Ridge(alpha=alpha)
    )

    # Weight recent years more heavily (post-1980)
    weights = np.where(train_data["year"] >= 1980, 3.0, 1.0)
    model.fit(X, y, ridge__sample_weight=weights)
    return model


def poly_equation(model) -> str:
    """
    Extract a human-readable polynomial equation from a trained model.
    """
    lr = model.named_steps["ridge"]
    coefs = lr.coef_
    intercept = lr.intercept_

    terms = [f"{intercept:.6f}"]
    for i, c in enumerate(coefs, start=1):
        terms.append(f"{c:+.6f}*x^{i}")
    return "y = " + " ".join(terms)

def _make_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate consistent engineered features for the XGBoost model.
    """
    out = pd.DataFrame(index=df.index)
    yr = df["year"].astype(float)

    out["year_c"] = yr - _REF_YEAR
    out["year_c2"] = out["year_c"] ** 2
    out["anthro_c"] = df["anthropogenic_c"].astype(float)
    out["anthro_f"] = df["anthropogenic_f"].astype(float)
    out["co2_ppm"] = df["co2_ppm"].astype(float)
    out["ln_co2_ratio"] = df["ln_co2_ratio"].astype(float)
    return out


def train_xgb_residual(train_df: pd.DataFrame, poly_model):
    """
    Train an XGBoost regressor on the residuals of the polynomial trend model.
    """
    # Residuals = observed temperature - polynomial trend
    y_poly = poly_model.predict(train_df[["year"]])
    residuals = train_df["observed_c"].values - y_poly

    # Prepare engineered features
    X = _make_features(train_df)

    model = XGBRegressor(
        n_estimators=2000,
        learning_rate=0.01,
        max_depth=5,
        subsample=0.9,
        colsample_bytree=0.8,
        reg_lambda=1.0,
        tree_method="hist",
        random_state=42
    )

    model.fit(X, residuals, sample_weight=np.ones(len(X)), verbose=False)
    return model

def _calculate_metrics(y, yhat):
    """
    Calculate evaluation metrics for model predictions.
    """
    mse = mean_squared_error(y, yhat)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y, yhat)
    r2 = r2_score(y, yhat)
    resids = y - yhat
    return mse, rmse, mae, r2, resids


def evaluate_model(poly_model, xgb_model, df: pd.DataFrame, label: str):
    """
    Evaluate model performance.
    """
    X_poly = df[["year"]]
    trend_pred = poly_model.predict(X_poly)

    X_res = _make_features(df)
    resid_pred = xgb_model.predict(X_res)
    hybrid = trend_pred + resid_pred

    y_true = df["observed_c"].astype(float)

    # --- Trend-only evaluation ---
    mse, rmse, mae, r2, resids = _calculate_metrics(y_true, trend_pred)
    print(f"\n=== {label} (Trend-only) ===")
    print(f"MSE: {mse:.4f}  RMSE: {rmse:.4f}  MAE: {mae:.4f}  R²: {r2:.4f}")
    print(f"Residuals: mean={resids.mean():.4f}, std={resids.std():.4f}, "
          f"min={resids.min():.4f}, max={resids.max():.4f}")

    # --- Hybrid evaluation ---
    mse, rmse, mae, r2, resids = _calculate_metrics(y_true, hybrid)
    print(f"\n=== {label} (Hybrid) ===")
    print(f"MSE: {mse:.4f}  RMSE: {rmse:.4f}  MAE: {mae:.4f}  R²: {r2:.4f}")
    print(f"Residuals: mean={resids.mean():.4f}, std={resids.std():.4f}, "
          f"min={resids.min():.4f}, max={resids.max():.4f}")

    return trend_pred, hybrid

def predict_future(poly_model, xgb_model, df: pd.DataFrame, start: int, end: int):
    """
    Predict future global temperature anomalies (hybrid model).
    """
    years = np.arange(start, end + 1)
    poly_pred = poly_model.predict(years.reshape(-1, 1))

    # Estimate future CO₂ trend using exponential fit to recent history
    co2_hist = df[["year", "co2_ppm"]].dropna()
    recent = co2_hist[co2_hist["year"] >= 2010]
    slope = np.polyfit(recent["year"], np.log(recent["co2_ppm"]), 1)[0]
    co2_future = co2_hist["co2_ppm"].iloc[-1] * np.exp(slope * (years - co2_hist["year"].iloc[-1]))
    ln_co2_ratio = np.log(co2_future / 278.0)

    # Extrapolate anthropogenic components
    future_df = pd.DataFrame({
        "year": years,
        "anthropogenic_c": np.linspace(df["anthropogenic_c"].iloc[-15:].mean(),
                                       df["anthropogenic_c"].iloc[-1] + 0.5, len(years)),
        "anthropogenic_f": np.linspace(df["anthropogenic_f"].iloc[-15:].mean(),
                                       df["anthropogenic_f"].iloc[-1] + 0.5, len(years)),
        "co2_ppm": co2_future,
        "ln_co2_ratio": ln_co2_ratio
    })

    # Predict residuals and combine with polynomial baseline
    X = _make_features(future_df)
    resid_pred = xgb_model.predict(X)
    hybrid = poly_pred + resid_pred

    # Anchor to last observed data point
    last_obs = df.iloc[-1]["observed_c"]
    last_model = (
        poly_model.predict([[df.iloc[-1]["year"]]]) +
        xgb_model.predict(_make_features(df.iloc[[-1]]))
    )[0]
    offset = last_obs - last_model
    anchored = hybrid + offset

    return years, co2_future, poly_pred, hybrid, anchored