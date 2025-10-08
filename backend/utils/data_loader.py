"""
Data loading and preprocessing utilities for the Climate Change Prediction project.
"""

import pandas as pd
import numpy as np


def load_csv(path: str, columns: list = None, rename: dict = None) -> pd.DataFrame:
    """
    Load a CSV file and optionally select and rename columns.
    """
    df = pd.read_csv(path, comment="#")
    if columns:
        df = df[columns]
    if rename:
        df = df.rename(columns=rename)
    return df.sort_values("year").reset_index(drop=True)


def load_main(path: str) -> pd.DataFrame:
    """
    Load the main dataset (e.g., global temperature anomalies, anthropogenic data).
    """
    return load_csv(path)


def load_co2(path: str) -> pd.DataFrame:
    """
    Load atmospheric CO₂ concentration data and rename columns.
    """
    return load_csv(path, columns=["year", "ppm"], rename={"ppm": "co2_ppm"})


def merge_datasets(main_df: pd.DataFrame, co2_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge main dataset with CO₂ dataset and compute additional derived features.
    """
    df = main_df.merge(co2_df, on="year", how="left")
    df["ln_co2_ratio"] = np.log(df["co2_ppm"] / 278.0)  # Add forcing proxy
    return df


def split_data(df: pd.DataFrame):
    """
    Split dataset into training, validation, and testing subsets.
    """
    train = df[df["year"] <= 2005].copy()
    val = df[(df["year"] >= 2006) & (df["year"] <= 2015)].copy()
    test = df[df["year"] >= 2016].copy()
    return train, val, test