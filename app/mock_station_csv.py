"""
Shared loader for the real HCDP "partial station data" CSVs used as mock
data before a live OAUTH_TOKEN is available (see data_function.py, temp.py,
humidity.py). These are real station observations downloaded directly from
the HCDP portal in the same wide format the API would return, covering
Jan-Jul 2026.

Expected files live in hi-climate-backend/mock_data, named like:
  rainfall_new_day_statewide_partial_station_data_2026_04.csv
  rainfall_new_month_statewide_partial_station_data_2026.csv
  temperature_max_day_statewide_partial_station_data_2026_04.csv
  temperature_max_month_statewide_partial_station_data_2026.csv
  temperature_min_day_statewide_partial_station_data_2026_04.csv
  temperature_min_month_statewide_partial_station_data_2026.csv
  relative_humidity_day_statewide_partial_station_data_2026_04.csv
  (no relative_humidity monthly file)
"""

import os
from datetime import datetime
import pandas as pd

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
MOCK_DATA_DIR = os.path.normpath(
    os.path.join(_APP_DIR, "..", "..", "hi-climate-backend", "mock_data")
)

# Only Jan-Jul 2026 was downloaded; any requested month gets mapped onto
# this range so the mock data works regardless of what date is entered.
_AVAILABLE_MONTHS = 7

ISLAND_CODES = {
    "Hawaii (Big Island)": "BI",
    "Maui": "MA",
    "Oahu": "OA",
    "Kauai": "KA",
    "Molokai": "MO",
    "Lānai": "LA",
}


def available_month(requested_month: int) -> int:
    """Maps an arbitrary requested month (1-12) onto the available 1-7 range."""
    return ((requested_month - 1) % _AVAILABLE_MONTHS) + 1


def _day_file(prefix, month):
    return os.path.join(MOCK_DATA_DIR, f"{prefix}_day_statewide_partial_station_data_2026_{month:02d}.csv")


def _month_file(prefix):
    return os.path.join(MOCK_DATA_DIR, f"{prefix}_month_statewide_partial_station_data_2026.csv")


def load_station_values(prefix, matched_island, month, day=None):
    """
    Loads real station lat/lon/value rows for one island for a given metric.

    prefix: mock data file prefix, e.g. "rainfall_new", "temperature_max",
            "temperature_min", "relative_humidity"
    matched_island: full island name (a key in ISLAND_CODES)
    month: 1-7 (already mapped via available_month())
    day: if given, reads that single day's column from the daily file.
         If None, reads the monthly aggregate file (falling back to
         averaging the daily file across the month if no monthly file
         exists for this metric, e.g. humidity).

    Returns a list of {"lat": float, "lon": float, "value": float} dicts,
    one per station with a non-missing reading. Returns [] if the
    corresponding mock file/column/island isn't available.
    """
    island_code = ISLAND_CODES.get(matched_island)
    if not island_code:
        return []

    if day is not None:
        # Clamp so callers can pass any day-of-month (29-31 don't exist in
        # every month) without needing to know the mock data's calendar.
        day = min(day, 28)
        path = _day_file(prefix, month)
        col = f"X2026.{month:02d}.{day:02d}"
        return _read_column(path, island_code, col)

    month_path = _month_file(prefix)
    col = f"X2026.{month:02d}"
    if os.path.exists(month_path):
        records = _read_column(month_path, island_code, col)
        if records:
            return records

    # No monthly file for this metric (e.g. humidity) - average the days instead
    day_path = _day_file(prefix, month)
    if not os.path.exists(day_path):
        return []
    df = pd.read_csv(day_path)
    date_cols = [c for c in df.columns if c.startswith(f"X2026.{month:02d}.")]
    if not date_cols:
        return []
    subset = df[df["Island"] == island_code][["LAT", "LON"] + date_cols]
    records = []
    for _, row in subset.iterrows():
        values = row[date_cols].dropna()
        if len(values) == 0:
            continue
        records.append({"lat": float(row["LAT"]), "lon": float(row["LON"]), "value": float(values.mean())})
    return records


def find_nearest_station(prefix, latitude, longitude):
    """
    Finds the real mock station (statewide, any island) closest to the
    given lat/lon, using month 1's daily file as the station directory.

    Returns the station's SKN identifier, or None if no mock data exists.
    """
    path = _day_file(prefix, 1)
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path).dropna(subset=["LAT", "LON"])
    if df.empty:
        return None
    dist = (df["LAT"] - latitude) ** 2 + (df["LON"] - longitude) ** 2
    return df.loc[dist.idxmin(), "SKN"]


def load_station_daily_series(prefix, skn):
    """
    Loads one station's real daily readings across all available mock
    months (1-7), for use as a real (if short) time series - e.g. for
    training a forecast model. Returns a list of
    {"date": datetime, "value": float} sorted by date, skipping missing days.
    """
    records = []
    for month in range(1, _AVAILABLE_MONTHS + 1):
        path = _day_file(prefix, month)
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)
        row = df[df["SKN"] == skn]
        if row.empty:
            continue
        row = row.iloc[0]
        date_cols = [c for c in df.columns if c.startswith(f"X2026.{month:02d}.")]
        for col in date_cols:
            value = row[col]
            if pd.isna(value):
                continue
            day = int(col.rsplit(".", 1)[-1])
            records.append({"date": datetime(2026, month, day), "value": float(value)})
    records.sort(key=lambda r: r["date"])
    return records


def _read_column(path, island_code, col):
    if not os.path.exists(path):
        return []
    df = pd.read_csv(path)
    if col not in df.columns:
        return []
    subset = df[df["Island"] == island_code][["LAT", "LON", col]].dropna()
    return [
        {"lat": float(row["LAT"]), "lon": float(row["LON"]), "value": float(row[col])}
        for _, row in subset.iterrows()
    ]
