"""
Trains a RandomForestRegressor to predict next-day temperature from
(day_of_year, humidity, pressure, wind_speed, temperature).

Run:
    python train_model.py
"""
import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from data.generate_synthetic_data import generate

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "historical_weather.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "weather_model.pkl")

FEATURES = ["day_of_year", "humidity", "pressure", "wind_speed", "temperature"]
TARGET = "next_day_temperature"


def load_data():
    if not os.path.exists(DATA_PATH):
        df = generate()
        df.to_csv(DATA_PATH, index=False)
    else:
        df = pd.read_csv(DATA_PATH)
    return df


def train():
    df = load_data()
    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    print(f"MAE: {mae:.2f} °C")
    print(f"R2 score: {r2:.3f}")

    joblib.dump({"model": model, "features": FEATURES}, MODEL_PATH)
    print(f"Model saved -> {MODEL_PATH}")


if __name__ == "__main__":
    train()
