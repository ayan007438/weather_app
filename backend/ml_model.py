"""
Loads the trained model and exposes a simple predict_multi_day() function
that forecasts temperature for the next N days by iteratively feeding the
model's own output back in as the "current temperature" for the next step.

This is a lightweight recursive forecasting approach, appropriate for a
final-year-project demo. For production-grade forecasting you'd want a
proper time-series model (ARIMA, Prophet, or an LSTM).
"""
import os
import joblib
import numpy as np
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "weather_model.pkl")

_bundle = None


def _load():
    global _bundle
    if _bundle is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "weather_model.pkl not found. Run `python train_model.py` first."
            )
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


def predict_multi_day(day_of_year, humidity, pressure, wind_speed, temperature, days=5):
    """
    Returns a list of dicts: [{"day_offset": 1, "predicted_temp": 27.4}, ...]
    """
    bundle = _load()
    model = bundle["model"]
    features = bundle["features"]

    predictions = []
    cur_day = day_of_year
    cur_humidity = humidity
    cur_pressure = pressure
    cur_wind = wind_speed
    cur_temp = temperature

    for offset in range(1, days + 1):
        row = {
            "day_of_year": cur_day,
            "humidity": cur_humidity,
            "pressure": cur_pressure,
            "wind_speed": cur_wind,
            "temperature": cur_temp,
        }
        X = pd.DataFrame([[row[f] for f in features]], columns=features)
        next_temp = float(model.predict(X)[0])

        predictions.append({
            "day_offset": offset,
            "predicted_temp": round(next_temp, 1),
        })

        # Roll state forward for the next iteration
        cur_temp = next_temp
        cur_day = cur_day + 1 if cur_day < 365 else 1
        # small random-walk drift on humidity/wind/pressure to keep things plausible
        cur_humidity = float(np.clip(cur_humidity + np.random.normal(0, 1.5), 30, 95))
        cur_pressure = cur_pressure + np.random.normal(0, 0.8)
        cur_wind = max(0.0, cur_wind + np.random.normal(0, 0.8))

    return predictions
