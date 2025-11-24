import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
Driver script that loads historical climate data, trains the hybrid
polynomial + XGBoost pipeline, and prints future temperature projections.
"""

from backend.utils.data_loader import (
    load_main,
    load_co2,
    load_sea_level,
    merge_datasets,
    merge_with_sea_level,
    split_data,
    save_predictions,
)
from backend.model.temprature_model import (
    train_poly_model,
    train_xgb_residual,
    poly_equation,
    predict_future,
)
from backend.model.sea_level_model import (
    train_sea_poly_model,
    train_sea_xgb_residual,
    predict_sea_future,
)


if __name__ == "__main__":
    # Ingest historical temperature and CO₂ observations directly from SQLite
    main_df = load_main()
    co2_df = load_co2()
    data = merge_datasets(main_df, co2_df)  # Supplies ln(CO₂) forcing proxy

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
    save_predictions(future_years, anchored, table_name="future_predictions")

    # Present the final deterministic forecast in the console
    print("\nFuture Predictions")
    for y, h in zip(future_years, anchored):
        print(f"{y}: Temp={h:.2f}")

    print("\nProjection Summary:")
    print(f"  Min forecast: {anchored.min():.2f} °C in {future_years[anchored.argmin()]}")
    print(f"  Max forecast: {anchored.max():.2f} °C in {future_years[anchored.argmax()]}")

    # -------- Sea Level Pipeline -------- #
    sea_df = load_sea_level()
    sea_dataset = (
        merge_with_sea_level(data, sea_df).sort_values("year").reset_index(drop=True)
    )
    sea_train, sea_val, sea_test = split_data(sea_dataset)

    sea_poly = train_sea_poly_model(sea_train)
    sea_xgb = train_sea_xgb_residual(sea_train, sea_poly)

    sea_years, sea_poly_pred, sea_hybrid, sea_anchored = predict_sea_future(
        sea_poly, sea_xgb, sea_dataset, future_years, anchored
    )

    save_predictions(sea_years, sea_anchored, table_name="sea_level_predictions")

    print("\nSea Level Projections")
    for y, lvl in zip(sea_years, sea_anchored):
        print(f"{y}: GMSL={lvl:.2f} mm")