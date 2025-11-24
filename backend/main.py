import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
Driver script that loads historical climate data, trains the hybrid
polynomial + XGBoost pipeline, and prints future temperature projections.
"""

from backend.utils.data_loader import (
    load_main,
    load_co2,
    merge_datasets,
    split_data,
    save_predictions,
)
from backend.model.temprature_model import (
    train_poly_model,
    train_xgb_residual,
    poly_equation,
    predict_future
)


if __name__ == "__main__":
    # Ingest historical temperature and CO₂ observations directly from SQLite
    main_df = load_main()
    co2_df = load_co2()
    data = merge_datasets(main_df, co2_df)

    # Reserve earlier years for training and keep recent periods for holdout checks
    train, val, test = split_data(data)

    # Fit the long-term polynomial warming trend
    poly = train_poly_model(train, degree=2)

    # Learn residual structure that the polynomial baseline misses
    xgb = train_xgb_residual(train, poly)

    # Generate anchored projections for the coming decades
    future_years, co2_future, poly_pred, hybrid_pred, anchored = predict_future(
        poly, xgb, data, start=2025, end=2050
    )

    # Persist the latest projection run so other components can query it
    save_predictions(future_years, anchored)

    # Present the final deterministic forecast in the console
    print("\nFuture Predictions")
    for y, h in zip(future_years, anchored):
        print(f"{y}: Temp={h:.2f}")

    print("\nProjection Summary:")
    print(f"  Min forecast: {anchored.min():.2f} °C in {future_years[anchored.argmin()]}")
    print(f"  Max forecast: {anchored.max():.2f} °C in {future_years[anchored.argmax()]}")