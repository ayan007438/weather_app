const API_BASE = "http://localhost:5000/api";

const els = {
  form: document.getElementById("searchForm"),
  cityInput: document.getElementById("cityInput"),
  heroCity: document.getElementById("heroCity"),
  dialTemp: document.getElementById("dialTemp"),
  dialCond: document.getElementById("dialCond"),
  dialFill: document.getElementById("dialFill"),
  statFeels: document.getElementById("statFeels"),
  statHumidity: document.getElementById("statHumidity"),
  statPressure: document.getElementById("statPressure"),
  statWind: document.getElementById("statWind"),
  forecastStrip: document.getElementById("forecastStrip"),
  recGrid: document.getElementById("recGrid"),
  toast: document.getElementById("toast"),
};

let predictChart = null;

const CONDITION_ICON = {
  clear: "☀️", clouds: "☁️", rain: "🌧️", drizzle: "🌦️",
  thunderstorm: "⛈️", snow: "❄️", mist: "🌫️", fog: "🌫️", haze: "🌫️",
};

function iconFor(condition) {
  return CONDITION_ICON[(condition || "").toLowerCase()] || "🌡️";
}

function showToast(msg) {
  els.toast.textContent = msg;
  els.toast.classList.add("show");
  setTimeout(() => els.toast.classList.remove("show"), 3500);
}

async function fetchJSON(url) {
  const res = await fetch(url);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

function setDial(temp) {
  // Map -10..45 C onto the 0..270deg arc (circumference portion ~ 603 for r=96, but we
  // use the full 603 circumference and just vary the visible fraction for simplicity)
  const CIRC = 2 * Math.PI * 96; // ~603
  const min = -10, max = 45;
  const clamped = Math.max(min, Math.min(max, temp));
  const frac = (clamped - min) / (max - min);
  const offset = CIRC - frac * CIRC;
  els.dialFill.style.strokeDasharray = `${CIRC}`;
  els.dialFill.style.strokeDashoffset = `${offset}`;

  let color = "#F2A65A";
  if (temp <= 10) color = "#4FD1C5";
  else if (temp >= 32) color = "#F27C6D";
  els.dialFill.style.stroke = color;

  els.dialTemp.textContent = `${Math.round(temp)}°`;
}

async function loadCurrent(city) {
  const d = await fetchJSON(`${API_BASE}/current?city=${encodeURIComponent(city)}`);
  els.heroCity.textContent = `${d.city}${d.country ? ", " + d.country : ""}`;
  els.dialCond.textContent = d.description;
  setDial(d.temperature);
  els.statFeels.textContent = `${Math.round(d.feels_like)}°C`;
  els.statHumidity.textContent = `${d.humidity}%`;
  els.statPressure.textContent = `${d.pressure} hPa`;
  els.statWind.textContent = `${d.wind_speed} m/s`;
  return d;
}

async function loadForecast(city) {
  const d = await fetchJSON(`${API_BASE}/forecast?city=${encodeURIComponent(city)}`);
  els.forecastStrip.innerHTML = "";
  d.forecast.forEach(day => {
    const card = document.createElement("div");
    card.className = "forecast-card";
    const dayName = new Date(day.date).toLocaleDateString(undefined, { weekday: "short" });
    card.innerHTML = `
      <div class="forecast-day">${dayName.toUpperCase()}</div>
      <div class="forecast-icon">${iconFor(day.condition)}</div>
      <div class="forecast-cond">${day.condition}</div>
      <div class="forecast-range"><span class="max">${Math.round(day.temp_max)}°</span><span class="min">${Math.round(day.temp_min)}°</span></div>
    `;
    els.forecastStrip.appendChild(card);
  });
}

async function loadPrediction(city) {
  const d = await fetchJSON(`${API_BASE}/predict?city=${encodeURIComponent(city)}&days=5`);
  const labels = d.predictions.map(p => `+${p.day_offset}d`);
  const values = d.predictions.map(p => p.predicted_temp);

  const ctx = document.getElementById("predictChart").getContext("2d");
  if (predictChart) predictChart.destroy();
  predictChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Predicted temp (°C)",
        data: values,
        borderColor: "#F2A65A",
        backgroundColor: "rgba(242,166,90,0.15)",
        tension: 0.35,
        fill: true,
        pointBackgroundColor: "#F2A65A",
        pointRadius: 4,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: "#8CA3BE", font: { family: "IBM Plex Mono", size: 11 } } } },
      scales: {
        x: { ticks: { color: "#8CA3BE", font: { family: "IBM Plex Mono", size: 11 } }, grid: { color: "#24374F" } },
        y: { ticks: { color: "#8CA3BE", font: { family: "IBM Plex Mono", size: 11 } }, grid: { color: "#24374F" } },
      }
    }
  });
}

async function loadRecommendations(city) {
  const d = await fetchJSON(`${API_BASE}/recommend?city=${encodeURIComponent(city)}`);
  const r = d.recommendations;
  const sections = [
    { key: "clothing", title: "Clothing", cls: "" },
    { key: "activities", title: "Activities", cls: "cool" },
    { key: "health", title: "Health", cls: "alert" },
    { key: "travel", title: "Travel & Agriculture", cls: "cool" },
  ];
  els.recGrid.innerHTML = "";
  sections.forEach(s => {
    const card = document.createElement("div");
    card.className = `rec-card ${s.cls}`;
    card.innerHTML = `
      <div class="rec-title">${s.title}</div>
      <ul>${(r[s.key] || []).map(item => `<li>${item}</li>`).join("")}</ul>
    `;
    els.recGrid.appendChild(card);
  });
}

els.form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const city = els.cityInput.value.trim();
  if (!city) return;

  try {
    await loadCurrent(city);
    await Promise.all([
      loadForecast(city),
      loadPrediction(city),
      loadRecommendations(city),
    ]);
  } catch (err) {
    showToast(err.message || "Something went wrong");
  }
});
