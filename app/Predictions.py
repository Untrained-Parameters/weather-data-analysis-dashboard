import json
import os
import requests
import pandas as pd
import plotly.graph_objects as go
from shapely.geometry import Point
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import streamlit as st
import mock_station_csv

# Load environment variables from .env file. override=True because
# Streamlit pre-populates MAPBOX_API_KEY as an empty string from its own
# config system before this ever runs, and load_dotenv() otherwise leaves
# already-set variables alone - silently ignoring the real value in .env.
load_dotenv(override=True)


def _generate_mock_rainfall_forecast_plot(month: str, latitude: float, longitude: float):
    """
    Builds an actual-vs-predicted rainfall plot for demo/screenshot purposes
    when no live OAUTH_TOKEN is configured yet, using a real nearby station's
    real daily rainfall readings (see mock_station_csv.py) both as the
    "actual" series and as training data for a real forecast model. Only
    Jan-Jul 2026 was downloaded, so the requested month is mapped onto that
    range, and the model is trained on far less history than the live path
    (7 months instead of 36) - it stops being used automatically once a
    real OAUTH_TOKEN is set in .env.
    """
    skn = mock_station_csv.find_nearest_station("rainfall_new", latitude, longitude)
    if skn is None:
        raise ValueError("No mock station data available.")

    series = mock_station_csv.load_station_daily_series("rainfall_new", skn)
    if not series:
        raise ValueError("No mock rainfall data available for the nearest station.")

    df_actual = pd.DataFrame(series).rename(columns={"value": "rainfall"})

    df_train = df_actual.copy()
    df_train["day"] = df_train["date"].dt.day
    df_train["month"] = df_train["date"].dt.month

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(df_train[["day", "month"]], df_train["rainfall"])

    requested_month = datetime.strptime("01/" + month, "%d/%m/%Y").month
    target_month = mock_station_csv.available_month(requested_month)
    forecast_dates = [datetime(2026, target_month, day) for day in range(1, 29)]
    df_forecast = pd.DataFrame({
        "date": forecast_dates,
        "day": [d.day for d in forecast_dates],
        "month": [d.month for d in forecast_dates],
    })
    df_forecast["predicted_rainfall"] = model.predict(df_forecast[["day", "month"]])

    _plot_actual_vs_predicted(df_actual, df_forecast)


def generate_rainfall_forecast_plot(month: str, latitude: float, longitude: float):
    """
    Generate and display a Plotly chart of actual vs predicted daily rainfall.

    Forecast range: Apr 4, 2025 to end of input month.
    Actuals: Dec 2024 to end of input month.

    Parameters:
        month (str): "MM/YYYY" format (e.g., "06/2025")
        latitude (float): Latitude of location
        longitude (float): Longitude of location
    """

    # Read the API token from the environment variable. If it's not set
    # yet, fall back to real downloaded HCDP station data (see
    # mock_station_csv.py) so the app is still usable for demos before a
    # real HCDP token is available.
    hcdp_api_token = os.getenv("OAUTH_TOKEN")
    if not hcdp_api_token:
        return _generate_mock_rainfall_forecast_plot(month, latitude, longitude)

    api_base_url = "https://api.hcdp.ikewai.org"
    header = {"Authorization": f"Bearer {hcdp_api_token}"}

    def query_stations(values, name, limit=10000, offset=0):
        params = {"name": name}
        for key in values:
            params[f"value.{key}"] = values[key]
        params = {"q": json.dumps(params), "limit": limit, "offset": offset}
        url = f"{api_base_url}/stations"
        res = requests.get(url, params=params, headers=header)
        res.raise_for_status()
        return [item["value"] for item in res.json()["result"]]

    def get_station_metadata():
        res = query_stations({}, name="hcdp_station_metadata")
        return {m[m["id_field"]]: m for m in res}

    def get_closest_station_id(lat, lon, metadata):
        point = Point(lon, lat)
        closest_station, min_dist = None, float("inf")
        for sid, meta in metadata.items():
            try:
                station_point = Point(float(meta["lng"]), float(meta["lat"]))
                dist = point.distance(station_point)
                if dist < min_dist:
                    min_dist = dist
                    closest_station = sid
            except:
                continue
        return closest_station

    now = datetime(2025, 4, 6)
    target_month = datetime.strptime("01/" + month, "%d/%m/%Y")
    forecast_start = datetime(2025, 4, 4)
    forecast_end = (target_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    train_start = forecast_start - relativedelta(months=36)
    train_end = forecast_start - timedelta(days=1)

    actual_start = datetime(2024, 12, 1)
    actual_end = forecast_end

    metadata = get_station_metadata()
    station_id = get_closest_station_id(latitude, longitude, metadata)
    if not station_id:
        raise ValueError("No nearby station found.")

    values_train = {
        "station_id": station_id,
        "datatype": "rainfall",
        "production": "new",
        "period": "day",
        "fill": "partial",
        "date": {
            "$gte": train_start.strftime("%Y-%m-%d"),
            "$lte": train_end.strftime("%Y-%m-%d")
        }
    }
    train_raw = query_stations(values_train, name="hcdp_station_value")
    df_train = pd.DataFrame([
        {
            "date": datetime.strptime(r["date"], "%Y-%m-%d"),
            "day": datetime.strptime(r["date"], "%Y-%m-%d").day,
            "month": datetime.strptime(r["date"], "%Y-%m-%d").month,
            "year": datetime.strptime(r["date"], "%Y-%m-%d").year,
            "rainfall": float(r["value"])
        }
        for r in train_raw if "value" in r
    ])

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(df_train[["day", "month", "year"]], df_train["rainfall"])

    forecast_dates = [forecast_start + timedelta(days=i) for i in range((forecast_end - forecast_start).days + 1)]
    df_forecast = pd.DataFrame({
        "date": forecast_dates,
        "day": [d.day for d in forecast_dates],
        "month": [d.month for d in forecast_dates],
        "year": [d.year for d in forecast_dates]
    })
    df_forecast["predicted_rainfall"] = model.predict(df_forecast[["day", "month", "year"]])

    values_actual = {
        "station_id": station_id,
        "datatype": "rainfall",
        "production": "new",
        "period": "day",
        "fill": "partial",
        "date": {
            "$gte": actual_start.strftime("%Y-%m-%d"),
            "$lte": actual_end.strftime("%Y-%m-%d")
        }
    }
    actual_raw = query_stations(values_actual, name="hcdp_station_value")
    df_actual = pd.DataFrame([
        {
            "date": datetime.strptime(r["date"], "%Y-%m-%d"),
            "rainfall": float(r["value"])
        }
        for r in actual_raw if "value" in r
    ]).sort_values("date")

    _plot_actual_vs_predicted(df_actual, df_forecast)


def _plot_actual_vs_predicted(df_actual, df_forecast):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_actual["date"],
        y=df_actual["rainfall"],
        mode='lines+markers',
        name='Actual Rainfall',
        line=dict(width=3)
    ))

    fig.add_trace(go.Scatter(
        x=df_forecast["date"],
        y=df_forecast["predicted_rainfall"],
        mode='lines+markers',
        name='Predicted Rainfall',
        line=dict(width=3)
    ))

    fig.update_layout(
        title=dict(
            text="Actual vs Predicted Daily Rainfall",
            font=dict(size=25)
        ),
        xaxis=dict(
            title=dict(text="Date", font=dict(size=24)),
            tickfont=dict(size=20),
            showgrid=False
        ),
        yaxis=dict(
            title=dict(text="Rainfall (mm)", font=dict(size=24)),
            tickfont=dict(size=20),
            showgrid=False
        ),
        legend=dict(
            x=0.01,
            y=0.99,
            font=dict(size=20)
        ),
        font=dict(size=18),  # Base font size
        template='plotly_white',
        height=500
    )

    st.plotly_chart(fig)