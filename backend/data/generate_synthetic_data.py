"""
Generates a synthetic 5-year daily weather dataset used to train the
demonstration ML model.

IMPORTANT (for your final year report):
This synthetic generator exists so the project runs end-to-end without
needing you to source a real dataset first. For a stronger submission,
replace this with a real historical dataset for your target city, e.g.:
  - Kaggle "Historical Weather Data" sets
  - NOAA / Meteostat (https://meteostat.net) historical CSV exports
  - Visual Crossing Weather API historical endpoint

Just make sure the final CSV has the same columns used below
(day_of_year, humidity, pressure, wind_speed, temperature) and re-run
train_model.py.
"""
import numpy as np
import pandas as pd
import os

np.random.seed(42)

N_YEARS = 5
DAYS = 365 * N_YEARS

def generate():
    day_of_year = np.tile(np.arange(1, 366), N_YEARS)

    # Seasonal temperature curve (sinusoidal) + noise
    base_temp = 22 + 10 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
    temp_noise = np.random.normal(0, 2.2, DAYS)
    temperature = base_temp + temp_noise

    # Humidity inversely related to temperature swings, bounded 30-95
    humidity = 70 - 0.6 * (temperature - 22) + np.random.normal(0, 6, DAYS)
    humidity = np.clip(humidity, 30, 95)

    # Pressure with mild seasonal drift
    pressure = 1013 + 4 * np.sin(2 * np.pi * (day_of_year - 30) / 365) + np.random.normal(0, 3, DAYS)

    # Wind speed loosely random, slightly higher in transitional months
    wind_speed = 8 + 4 * np.abs(np.sin(2 * np.pi * day_of_year / 365)) + np.random.normal(0, 2, DAYS)
    wind_speed = np.clip(wind_speed, 0, None)

    # Next-day temperature target (what we ultimately want to predict)
    next_day_temp = np.roll(temperature, -1)

    df = pd.DataFrame({
        "day_of_year": day_of_year,
        "humidity": humidity.round(1),
        "pressure": pressure.round(1),
        "wind_speed": wind_speed.round(1),
        "temperature": temperature.round(1),
        "next_day_temperature": next_day_temp.round(1),
    })

    # Drop the wrap-around last row (roll artifact)
    df = df.iloc[:-1]
    return df

if __name__ == "__main__":
    df = generate()
    out_path = os.path.join(os.path.dirname(__file__), "historical_weather.csv")
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} rows -> {out_path}")
