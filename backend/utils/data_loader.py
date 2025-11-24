"""
Utility helpers for ingesting historical data from the SQLite datastore and
preparing merged climate datasets.
"""

from pathlib import Path
import sqlite3

import pandas as pd
import numpy as np

_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "climate.db"


def set_db_path(path: str | Path) -> None:
    """
    Allow tests/scripts to override the default database location.
    """
    global _DB_PATH
    _DB_PATH = Path(path)


def _read_table(table: str, columns: list[str] | None = None) -> pd.DataFrame:
    """
    Pull a table (or subset of columns) from SQLite into a pandas DataFrame.
    """
    projection = ", ".join(columns) if columns else "*"
    query = f"SELECT {projection} FROM {table}"
    with sqlite3.connect(_DB_PATH) as conn:
        df = pd.read_sql_query(query, conn)
    return df.sort_values("year").reset_index(drop=True)


def load_main() -> pd.DataFrame:
    """
    Load the temperature and anthropogenic forcing measurements.
    """
    return _read_table("temperature")


def load_co2() -> pd.DataFrame:
    """
    Load atmospheric CO₂ concentration data (already labeled co2_ppm).
    """
    return _read_table("co2_concentration", columns=["year", "co2_ppm"])


def load_sea_level() -> pd.DataFrame:
    """
    Load the recorded global mean sea level (gmsl) measurements.
    """
    return _read_table("sea_level", columns=["year", "gmsl"])


def merge_datasets(main_df: pd.DataFrame, co2_df: pd.DataFrame) -> pd.DataFrame:
    """
    Join the temperature and CO₂ tables while computing logarithmic forcing proxies.
    """
    df = main_df.merge(co2_df, on="year", how="left")
    df["ln_co2_ratio"] = np.log(df["co2_ppm"] / 278.0)  # Add forcing proxy
    return df


def merge_with_sea_level(temp_df: pd.DataFrame, sea_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge the temperature dataset with sea-level observations.
    """
    return temp_df.merge(sea_df, on="year", how="inner")


def split_data(df: pd.DataFrame):
    """
    Slice the merged dataset into train/validation/test windows for evaluation.
    """
    train = df[df["year"] <= 2005].copy()
    val = df[(df["year"] >= 2006) & (df["year"] <= 2015)].copy()
    test = df[df["year"] >= 2016].copy()
    return train, val, test


def save_predictions(years, anchored_pred, table_name: str = "future_predictions"):
    """
    Persist future forecast results so downstream services can query them.
    """
    df = pd.DataFrame(
        {
            "year": years,
            "prediction": anchored_pred,
        }
    )

    with sqlite3.connect(_DB_PATH) as conn:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                year INTEGER PRIMARY KEY,
                prediction REAL
            )
            """
        )
        df.to_sql(table_name, conn, if_exists="replace", index=False)