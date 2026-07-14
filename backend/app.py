import os
import datetime
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from ml_model import predict_multi_day
from recommendation import get_recommendations

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"
GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)


def require_api_key():
    if not API_KEY:
        return jsonify({
            "error": "Server misconfigured: OPENWEATHER_API_KEY is missing. "
                     "Copy backend/.env.example to backend/.env and add your key."
        }), 500
    return None


def geocode_city(city):
    resp = requests.get(GEO_URL, params={"q": city, "limit": 1, "appid": API_KEY}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        return None
    return data[0]["lat"], data[0]["lon"], data[0].get("name", city), data[0].get("country", "")


@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/current")
def current_weather():
    err = require_api_key()
    if err:
        return err
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "Missing 'city' query parameter"}), 400

    try:
        resp = requests.get(
            f"{BASE_URL}/weather",
            params={"q": city, "appid": API_KEY, "units": "metric"},
            timeout=10,
        )
        resp.raise_for_status()
        d = resp.json()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch current weather: {e}"}), 502

    result = {
        "city": d.get("name"),
        "country": d.get("sys", {}).get("country"),
        "temperature": d["main"]["temp"],
        "feels_like": d["main"]["feels_like"],
        "humidity": d["main"]["humidity"],
        "pressure": d["main"]["pressure"],
        "wind_speed": d["wind"]["speed"],
        "condition": d["weather"][0]["main"],
        "description": d["weather"][0]["description"],
        "icon": d["weather"][0]["icon"],
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }
    return jsonify(result)


@app.route("/api/forecast")
def forecast():
    err = require_api_key()
    if err:
        return err
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "Missing 'city' query parameter"}), 400

    try:
        resp = requests.get(
            f"{BASE_URL}/forecast",
            params={"q": city, "appid": API_KEY, "units": "metric"},
            timeout=10,
        )
        resp.raise_for_status()
        d = resp.json()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch forecast: {e}"}), 502

    # OpenWeather free tier returns 3-hour steps; collapse to daily summaries
    daily = {}
    for entry in d.get("list", []):
        date = entry["dt_txt"].split(" ")[0]
        daily.setdefault(date, []).append(entry)

    daily_summary = []
    for date, entries in list(daily.items())[:5]:
        temps = [e["main"]["temp"] for e in entries]
        conditions = [e["weather"][0]["main"] for e in entries]
        daily_summary.append({
            "date": date,
            "temp_min": round(min(temps), 1),
            "temp_max": round(max(temps), 1),
            "condition": max(set(conditions), key=conditions.count),
            "humidity": round(sum(e["main"]["humidity"] for e in entries) / len(entries)),
        })

    return jsonify({"city": d.get("city", {}).get("name"), "forecast": daily_summary})


@app.route("/api/predict")
def predict():
    """
    ML-based multi-day temperature prediction, seeded from current
    real-world conditions.
    """
    err = require_api_key()
    if err:
        return err
    city = request.args.get("city", "").strip()
    days = int(request.args.get("days", 5))
    if not city:
        return jsonify({"error": "Missing 'city' query parameter"}), 400

    try:
        resp = requests.get(
            f"{BASE_URL}/weather",
            params={"q": city, "appid": API_KEY, "units": "metric"},
            timeout=10,
        )
        resp.raise_for_status()
        d = resp.json()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch seed weather: {e}"}), 502

    day_of_year = datetime.date.today().timetuple().tm_yday

    try:
        predictions = predict_multi_day(
            day_of_year=day_of_year,
            humidity=d["main"]["humidity"],
            pressure=d["main"]["pressure"],
            wind_speed=d["wind"]["speed"],
            temperature=d["main"]["temp"],
            days=days,
        )
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"city": d.get("name"), "predictions": predictions})


@app.route("/api/recommend")
def recommend():
    err = require_api_key()
    if err:
        return err
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "Missing 'city' query parameter"}), 400

    try:
        resp = requests.get(
            f"{BASE_URL}/weather",
            params={"q": city, "appid": API_KEY, "units": "metric"},
            timeout=10,
        )
        resp.raise_for_status()
        d = resp.json()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch weather: {e}"}), 502

    recs = get_recommendations(
        temp=d["main"]["temp"],
        humidity=d["main"]["humidity"],
        wind_speed=d["wind"]["speed"],
        condition=d["weather"][0]["main"],
    )
    return jsonify({"city": d.get("name"), "recommendations": recs})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port)
