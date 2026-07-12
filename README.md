# Aerovane — Weather Prediction & Recommendation System

A full-stack project: a Flask backend that fetches live weather
data, runs a machine-learning model to predict temperature for the next
few days, and generates rule-based recommendations (clothing, activities,
health, travel/agriculture). The frontend is a vanilla HTML/CSS/JS
dashboard styled as an "instrument panel."

## Architecture

```
weather-app/
├── backend/
│   ├── app.py                 Flask API (current, forecast, predict, recommend)
│   ├── ml_model.py             Loads trained model, runs recursive multi-day forecast
│   ├── recommendation.py       Rule-based recommendation engine
│   ├── train_model.py          Trains RandomForestRegressor on historical data
│   ├── data/
│   │   ├── generate_synthetic_data.py   Synthetic historical dataset (swap for real data)
│   │   └── historical_weather.csv       Generated on first run
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html
    ├── style.css
    └── script.js
```

## How it works

1. **Live data**: `app.py` calls the OpenWeatherMap API for current
   conditions and a 5-day/3-hour forecast, collapsed into daily summaries.
2. **Prediction**: `train_model.py` trains a `RandomForestRegressor` on a
   historical dataset (day-of-year, humidity, pressure, wind speed,
   temperature → next-day temperature). `ml_model.py` seeds the model with
   today's *real* observed weather, then recursively predicts forward
   5 days, feeding each prediction back in as the next day's input.
3. **Recommendations**: `recommendation.py` is a transparent, rule-based
   engine — easy to explain in a viva — mapping temperature, humidity,
   wind and condition to clothing/activity/health/travel advice.
4. **Frontend**: fetches all four endpoints and renders a dashboard with
   a temperature dial, forecast strip, a Chart.js prediction line chart,
   and recommendation cards.

## Setup

### 1. Get a free API key
Sign up at https://openweathermap.org/api and grab a free API key
(takes a few minutes to activate).

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and paste your OPENWEATHER_API_KEY

python train_model.py           # trains and saves weather_model.pkl
python app.py                   # starts the API on http://localhost:5000
```

### 3. Frontend

The Flask app already serves `frontend/` as static files, so once
`app.py` is running you can just open **http://localhost:5000** in your
browser. (Or open `frontend/index.html` directly — `script.js` points at
`http://localhost:5000/api`, and CORS is enabled either way.)

## Improving this for submission

- **Replace the synthetic dataset** (`data/generate_synthetic_data.py`)
  with a real historical dataset for your target city — Meteostat,
  NOAA, or a Kaggle weather dataset all work. Keep the same columns and
  re-run `train_model.py`.
- **Swap the recursive RandomForest** for a proper time-series model
  (Prophet, ARIMA, or an LSTM) if your course expects deep learning.
- **Add a database** (SQLite/PostgreSQL) to log every query and let you
  show a "prediction accuracy over time" chart — strong for a final-year
  demo.
- **Add user accounts** to save favorite cities and personalize
  recommendations (e.g. asthma-sensitive users get stronger air-quality
  warnings).
- **Deploy**: backend to Render/Railway/PythonAnywhere, frontend to
  Netlify/Vercel/GitHub Pages (update `API_BASE` in `script.js`).

## API reference

| Endpoint | Params | Returns |
|---|---|---|
| `GET /api/current` | `city` | Current temp, humidity, pressure, wind, condition |
| `GET /api/forecast` | `city` | 5-day daily min/max/condition summary |
| `GET /api/predict` | `city`, `days` (default 5) | ML-predicted temperatures for next N days |
| `GET /api/recommend` | `city` | Clothing / activity / health / travel recommendations |

## google_stitch_prompt.md

See that file for a ready-to-paste prompt for Google Stitch if you want
to (re)generate the UI design/mockups from scratch instead of using the
included HTML/CSS.
