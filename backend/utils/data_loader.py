"""
Utility helpers for ingesting CSV files and preparing merged climate datasets.
"""

import pandas as pd
import numpy as np


def load_csv(path: str, columns: list = None, rename: dict = None) -> pd.DataFrame:
    """
    Basic CSV loader that supports optional column selection and renaming.
    """
    df = pd.read_csv(path, comment="#")
    if columns:
        df = df[columns]
    if rename:
        df = df.rename(columns=rename)
    return df.sort_values("year").reset_index(drop=True)


def load_main(path: str) -> pd.DataFrame:
    """
    Pull the primary temperature and anthropogenic forcing dataset into memory.
    """
    return load_csv(path)


def load_co2(path: str) -> pd.DataFrame:
    """
    Read atmospheric CO₂ concentration records and normalize their column names.
    """
    return load_csv(path, columns=["year", "ppm"], rename={"ppm": "co2_ppm"})


def merge_datasets(main_df: pd.DataFrame, co2_df: pd.DataFrame) -> pd.DataFrame:
    """
    Join the temperature and CO₂ tables while computing logarithmic forcing proxies.
    """
    df = main_df.merge(co2_df, on="year", how="left")
    df["ln_co2_ratio"] = np.log(df["co2_ppm"] / 278.0)  # Add forcing proxy
    return df


def split_data(df: pd.DataFrame):
    """
    Slice the merged dataset into train/validation/test windows for evaluation.
    """
    train = df[df["year"] <= 2005].copy()
    val = df[(df["year"] >= 2006) & (df["year"] <= 2015)].copy()
    test = df[df["year"] >= 2016].copy()
    return train, val, test