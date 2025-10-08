"""
This script trains and evaluates a hybrid model to predict global temperature
anomalies based on CO₂ concentration and anthropogenic factors.
"""

import matplotlib.pyplot as plt
from data_loader import load_main, load_co2, merge_datasets, split_data
from temprature_model import (
    train_poly_model,
    train_xgb_residual,
    poly_equation,
    evaluate_model,
    predict_future
)


def display_dataset_summary(data, train, val, test):
    """
    Display a summary of the dataset splits.
    """
    print("\n=== Dataset Info ===")
    print(f"Years available: {data['year'].min()} → {data['year'].max()} (n={len(data)})")
    print(f"Train: {train['year'].min()}–{train['year'].max()} ({len(train)})")
    print(f"Val  : {val['year'].min()}–{val['year'].max()} ({len(val)})")
    print(f"Test : {test['year'].min()}–{test['year'].max()} ({len(test)})")
    print("Features:", list(data.columns))


def plot_future_predictions(data, future_years, anchored):
    """
    Plot observed data and future predictions.
    """
    plt.figure(figsize=(10, 6))

    # Scatter: observed data
    plt.scatter(data["year"], data["observed_c"], label="Observed", alpha=0.7)

    # Line: future predictions
    plt.plot(future_years, anchored, color="red", label="Future Projection")

    # Reference lines: Paris Agreement thresholds
    plt.axhline(1.5, color="orange", linestyle="--", label="Current Temp")
    plt.axhline(2.0, color="brown", linestyle="--", label="2.0°C Warning")

    # Chart formatting
    plt.xlabel("Year")
    plt.ylabel("Global Temperature (°C)")
    plt.title("Predicted Global Warming (2025–2050 Projection)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Define file paths
    main_path = r"c:\Users\Administrator\Desktop\ai thing\temp.csv"
    co2_path = r"c:\Users\Administrator\Desktop\ai thing\co2_concentration.csv"

    # Load and merge datasets
    main_df = load_main(main_path)
    co2_df = load_co2(co2_path)
    data = merge_datasets(main_df, co2_df)

    # Split into training, validation, and test sets
    train, val, test = split_data(data)

    # Display dataset summary
    display_dataset_summary(data, train, val, test)

    # Train Polynomial Trend Model
    poly = train_poly_model(train, degree=2)
    print("\n=== Polynomial Trend Model ===")
    print("Equation:", poly_equation(poly))

    # Train XGBoost Residual Model
    xgb = train_xgb_residual(train, poly)
    print("\n=== Residual XGBoost Model ===")
    print("Feature Importances:")
    for feat, imp in zip(
        ["year_c", "year_c2", "anthro_c", "anthro_f", "co2_ppm", "ln_co2_ratio"],
        xgb.feature_importances_
    ):
        print(f"  {feat}: {imp:.4f}")

    # Evaluate Model Performance
    evaluate_model(poly, xgb, train, "Training")
    evaluate_model(poly, xgb, val, "Validation")
    evaluate_model(poly, xgb, test, "Testing")

    # Predict Future Climate Trends (2025–2050)
    future_years, co2_future, poly_pred, predict, anchored = predict_future(
        poly, xgb, data, start=2025, end=2050
    )

    print("\n=== Future Predictions (Anchored) ===")
    for y, h in zip(future_years, anchored):
        print(f"{y}: Temp={h:.2f}")

    # Visualization
    plot_future_predictions(data, future_years, anchored)