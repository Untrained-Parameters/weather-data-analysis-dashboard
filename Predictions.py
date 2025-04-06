import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from dateutil.relativedelta import relativedelta

# ------------------------ CONFIG ------------------------

hcdp_api_token = "c8aebebea3d9684526cfdab0fc62cbd6"
api_base_url = "https://api.hcdp.ikewai.org"
header = {"Authorization": f"Bearer {hcdp_api_token}"}

# ------------------------ API UTILITIES ------------------------

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

# ------------------------ FORECAST FUNCTION ------------------------

def forecast_rainfall_last_36_months(month_year: str, lat: float, lon: float):
    """
    Train on the past 36 months of daily rainfall data,
    and predict rainfall from April 5th to the end of the input month.
    """
    target_month = datetime.strptime("01/" + month_year, "%d/%m/%Y")
    target_year, target_month_num = target_month.year, target_month.month

    train_start = target_month - relativedelta(months=36)
    train_end = target_month - timedelta(days=1)

    forecast_start = datetime(target_year, target_month_num, 3)
    forecast_end = (forecast_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    metadata = get_station_metadata()
    station_id = get_closest_station_id(lat, lon, metadata)
    if not station_id:
        raise ValueError("No nearby station found.")

    values = {
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

    try:
        results = query_stations(values, name="hcdp_station_value")
        training_data = [
            {
                "date": datetime.strptime(r["date"], "%Y-%m-%d"),
                "day": datetime.strptime(r["date"], "%Y-%m-%d").day,
                "month": datetime.strptime(r["date"], "%Y-%m-%d").month,
                "year": datetime.strptime(r["date"], "%Y-%m-%d").year,
                "rainfall": float(r["value"])
            }
            for r in results if "value" in r
        ]
    except Exception as e:
        print(f"Failed to fetch training data: {e}")
        return pd.DataFrame(), station_id

    if not training_data:
        raise ValueError("No training data available.")

    df_train = pd.DataFrame(training_data)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(df_train[["day", "month", "year"]], df_train["rainfall"])

    forecast_dates = [forecast_start + timedelta(days=i) for i in range((forecast_end - forecast_start).days + 1)]
    forecast_df = pd.DataFrame({
        "date": forecast_dates,
        "day": [d.day for d in forecast_dates],
        "month": [d.month for d in forecast_dates],
        "year": [d.year for d in forecast_dates]
    })

    forecast_df["predicted_rainfall"] = model.predict(forecast_df[["day", "month", "year"]])
    return forecast_df[["date", "predicted_rainfall"]], station_id

# ------------------------ ACTUAL DATA FUNCTION ------------------------

def get_actual_rainfall_data(lat, lon, start_month_str):
    """
    Fetch actual daily rainfall for the 4 months prior to and the month of the input date.
    Uses a single batch API call to speed up the request.
    """
    target_month = datetime.strptime("01/" + start_month_str, "%d/%m/%Y")
    start_range = target_month - relativedelta(months=4)
    end_range = (target_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    metadata = get_station_metadata()
    station_id = get_closest_station_id(lat, lon, metadata)
    if not station_id:
        raise ValueError("No nearby station found.")

    values = {
        "station_id": station_id,
        "datatype": "rainfall",
        "production": "new",
        "period": "day",
        "fill": "partial",
        "date": {
            "$gte": start_range.strftime("%Y-%m-%d"),
            "$lte": end_range.strftime("%Y-%m-%d")
        }
    }

    try:
        results = query_stations(values, name="hcdp_station_value")
        data = []
        for r in results:
            date = datetime.strptime(r["date"], "%Y-%m-%d")
            rainfall = float(r["value"])
            data.append({"date": date, "rainfall": rainfall})
        return pd.DataFrame(data).sort_values("date")
    except Exception as e:
        print(f"Failed to fetch actual rainfall data: {e}")
        return pd.DataFrame(columns=["date", "rainfall"])

# ------------------------ MAIN CALL + PLOT ------------------------

lat, lon = 21.688333, -157.952500
input_month = "04/2025"

df_forecast, _ = forecast_rainfall_last_36_months(input_month, lat, lon)
df_actual = get_actual_rainfall_data(lat, lon, input_month)

# Plot
plt.figure(figsize=(12, 6))
plt.plot(pd.to_datetime(df_actual["date"]), df_actual["rainfall"], label="Actual Rainfall (Past 5 Months)", linewidth=2)
plt.plot(df_forecast["date"], df_forecast["predicted_rainfall"], label=f"Predicted Rainfall ({input_month} from Apr 5)", linewidth=2)
plt.xlabel("Date")
plt.ylabel("Rainfall (mm)")
plt.title("Actual vs Predicted Daily Rainfall")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()