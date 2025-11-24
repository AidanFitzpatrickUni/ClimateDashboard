"""
Utility script to build the SQLite database used by the Climate Dashboard.

Reads the legacy CSV sources and persists them as normalized tables so the
runtime code can query SQLite instead of parsing CSVs on every execution.
"""

from pathlib import Path
import sqlite3

import pandas as pd


def build_database(db_path: Path | None = None) -> Path:
    """
    Create or refresh the SQLite database from the CSV files.
    """
    repo_root = Path(__file__).resolve().parents[1]
    data_dir = repo_root / "data"

    if db_path is None:
        db_path = data_dir / "climate.db"

    temp_path = data_dir / "temp.csv"
    co2_path = data_dir / "co2_concentration.csv"
    sea_path = data_dir / "ClimateChangeTracker.org_Data_Download_Chart_4_8.csv"

    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        temp_df = pd.read_csv(temp_path, comment="#")[
            ["year", "anthropogenic_c", "observed_c", "anthropogenic_f"]
        ]
        temp_df.to_sql("temperature", conn, if_exists="replace", index=False)

        co2_df = (
            pd.read_csv(co2_path, comment="#")[["year", "ppm"]]
            .rename(columns={"ppm": "co2_ppm"})
        )
        co2_df.to_sql("co2_concentration", conn, if_exists="replace", index=False)

        sea_df = pd.read_csv(sea_path, comment="#")[["year", "gmsl"]]
        sea_df.to_sql("sea_level", conn, if_exists="replace", index=False)

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_temperature_year ON temperature(year)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_co2_year ON co2_concentration(year)"
        )
        # Indices keep join/pivot queries fast when sampling long histories
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sea_level_year ON sea_level(year)")
    finally:
        conn.commit()
        conn.close()

    return db_path


if __name__ == "__main__":
    path = build_database()
    print(f"SQLite climate database written to {path}")

