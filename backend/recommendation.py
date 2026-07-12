"""
Rule-based recommendation engine.
Takes a weather snapshot and returns clothing, activity, health and
travel/agriculture recommendations. Deliberately rule-based (not ML) so
it's transparent and easy to explain/defend in a viva.
"""

def get_recommendations(temp, humidity, wind_speed, condition, uv_index=None, rain_prob=None):
    condition = (condition or "").lower()
    recs = {
        "clothing": [],
        "activities": [],
        "health": [],
        "travel": [],
    }

    # --- Clothing ---
    if temp <= 5:
        recs["clothing"].append("Heavy winter coat, gloves, and a woolen cap")
    elif temp <= 15:
        recs["clothing"].append("Jacket or sweater, closed shoes")
    elif temp <= 25:
        recs["clothing"].append("Light layers, a t-shirt with a light jacket for evenings")
    else:
        recs["clothing"].append("Light, breathable cotton clothing")

    if "rain" in condition or (rain_prob and rain_prob > 50):
        recs["clothing"].append("Carry an umbrella or raincoat")
    if wind_speed > 25:
        recs["clothing"].append("Windbreaker recommended, secure loose items outdoors")
    if uv_index and uv_index >= 6:
        recs["clothing"].append("Sunglasses and a hat for UV protection")

    # --- Activities ---
    if "storm" in condition or "thunder" in condition:
        recs["activities"].append("Avoid outdoor activities; thunderstorm risk")
    elif "rain" in condition or (rain_prob and rain_prob > 60):
        recs["activities"].append("Good day for indoor activities; carry rain gear if you go out")
    elif 18 <= temp <= 28 and wind_speed < 20:
        recs["activities"].append("Great conditions for outdoor sports, walking, or cycling")
    elif temp > 33:
        recs["activities"].append("Limit strenuous outdoor activity between 11am-4pm")
    else:
        recs["activities"].append("Generally fine for outdoor plans; check hourly forecast")

    # --- Health ---
    if humidity > 80 and temp > 28:
        recs["health"].append("High heat + humidity: stay hydrated, watch for heat exhaustion symptoms")
    if humidity < 30:
        recs["health"].append("Low humidity may cause dry skin/throat; drink water regularly")
    if uv_index and uv_index >= 8:
        recs["health"].append("Very high UV: apply SPF 30+ sunscreen, avoid peak sun hours")
    if "smoke" in condition or "haze" in condition or "dust" in condition:
        recs["health"].append("Air quality may be poor; sensitive groups should wear a mask outdoors")
    if not recs["health"]:
        recs["health"].append("No significant weather-related health risks today")

    # --- Travel / Agriculture ---
    if "fog" in condition or "mist" in condition:
        recs["travel"].append("Reduced visibility: drive carefully, allow extra travel time")
    if "rain" in condition or "storm" in condition:
        recs["travel"].append("Roads may be slippery; farmers should delay pesticide/fertilizer spraying")
    if 20 <= temp <= 30 and humidity < 70 and "rain" not in condition:
        recs["travel"].append("Favorable conditions for field work, irrigation, and harvesting")
    if not recs["travel"]:
        recs["travel"].append("No major travel or agricultural advisories")

    return recs
