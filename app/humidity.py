import pandas as pd
from datetime import datetime, timedelta
import mock_station_csv

# Island names match the polygons/matching logic used in data_function.py
# and temp.py.
_ISLAND_NAMES = list(mock_station_csv.ISLAND_CODES.keys()) + ["Niihau", "Kahoolawe"]


def get_station_data_for_period_humidity(date_input: str, island_name: str):
    """
    Fetches station-level relative humidity data for a given island and
    day/month, using real station data downloaded from HCDP (see
    mock_station_csv.py). There is no live HCDP-backed path for humidity
    in this app yet, so this always uses the downloaded mock data.

    Parameters:
    - date_input (str): Either "MM/YYYY" for full month or "MM/DD/YYYY" for a specific day
    - island_name (str): Name of the island (e.g., "Oahu", "Maui", "Lanai", etc.)

    Returns:
    - pd.DataFrame: columns Time, lat, lon, humidity
    """
    island_name = island_name.lower()
    matched_island = None
    for name in _ISLAND_NAMES:
        if island_name in name.lower():
            matched_island = name
            break
    if not matched_island:
        raise ValueError(f"Island '{island_name}' not recognized.")

    try:
        if len(date_input) == 7:  # MM/YYYY
            start_date = datetime.strptime("01/" + date_input, "%d/%m/%Y")
            end_date = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        elif len(date_input) == 10:  # MM/DD/YYYY
            start_date = datetime.strptime(date_input, "%m/%d/%Y")
            end_date = start_date
        else:
            raise ValueError("Date input must be in MM/YYYY or MM/DD/YYYY format.")
    except ValueError as e:
        raise ValueError(f"Date parsing failed: {e}")

    date_list = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    month = mock_station_csv.available_month(date_list[0].month)
    display_date = date_list[0].strftime("%m/%d/%Y")

    if len(date_list) == 1:
        # Daily view: real observations for that specific day
        stations = mock_station_csv.load_station_values("relative_humidity", matched_island, month, day=date_list[0].day)
    else:
        # Monthly view: no monthly humidity file was downloaded, so this
        # falls back to averaging the daily readings across the month
        # (handled inside mock_station_csv.load_station_values).
        stations = mock_station_csv.load_station_values("relative_humidity", matched_island, month)

    records = [
        {"Time": display_date, "lat": s["lat"], "lon": s["lon"], "humidity": s["value"]}
        for s in stations
    ]
    return pd.DataFrame(records)
