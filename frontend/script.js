const API_BASE = "http://127.0.0.1:5000/api";

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
    toast: document.getElementById("toast")
};

let predictChart = null;

const CONDITION_ICON = {
    clear: "☀️",
    clouds: "☁️",
    rain: "🌧️",
    drizzle: "🌦️",
    thunderstorm: "⛈️",
    snow: "❄️",
    mist: "🌫️",
    haze: "🌫️",
    fog: "🌫️"
};

function iconFor(condition) {
    return CONDITION_ICON[(condition || "").toLowerCase()] || "🌡️";
}

function showToast(message) {
    els.toast.textContent = message;
    els.toast.classList.add("show");

    setTimeout(() => {
        els.toast.classList.remove("show");
    }, 3000);
}

async function fetchJSON(url) {

    const response = await fetch(url);

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "Request failed");
    }

    return data;
}

function setDial(temp) {

    const circumference = 2 * Math.PI * 96;

    const min = -10;
    const max = 45;

    const value = Math.max(min, Math.min(max, temp));

    const percent = (value - min) / (max - min);

    els.dialFill.style.strokeDasharray = circumference;
    els.dialFill.style.strokeDashoffset =
        circumference - (percent * circumference);

    let color = "#F2A65A";

    if (temp <= 10) color = "#4FD1C5";
    if (temp >= 32) color = "#F27C6D";

    els.dialFill.style.stroke = color;

    els.dialTemp.textContent = `${Math.round(temp)}°`;
}

async function loadCurrent(city) {

    const data = await fetchJSON(
        `${API_BASE}/current?city=${encodeURIComponent(city)}`
    );

    els.heroCity.textContent =
        `${data.city}${data.country ? ", " + data.country : ""}`;

    els.dialCond.textContent = data.description;

    setDial(data.temperature);

    els.statFeels.textContent = `${Math.round(data.feels_like)}°C`;
    els.statHumidity.textContent = `${data.humidity}%`;
    els.statPressure.textContent = `${data.pressure} hPa`;
    els.statWind.textContent = `${data.wind_speed} m/s`;
}

async function loadForecast(city) {

    const data = await fetchJSON(
        `${API_BASE}/forecast?city=${encodeURIComponent(city)}`
    );

    els.forecastStrip.innerHTML = "";

    data.forecast.forEach(day => {

        const card = document.createElement("div");

        card.className = "forecast-card";

        const weekday =
            new Date(day.date).toLocaleDateString(undefined, {
                weekday: "short"
            });

        card.innerHTML = `
            <div class="forecast-day">${weekday}</div>
            <div class="forecast-icon">${iconFor(day.condition)}</div>
            <div>${day.condition}</div>
            <div class="forecast-range">
                <span>${Math.round(day.temp_max)}°</span>
                <span>${Math.round(day.temp_min)}°</span>
            </div>
        `;

        els.forecastStrip.appendChild(card);

    });

}

async function loadPrediction(city) {

    const data = await fetchJSON(
        `${API_BASE}/predict?city=${encodeURIComponent(city)}&days=5`
    );

    console.log("Prediction:", data);

    if (!data.predictions || data.predictions.length === 0) {

        showToast("No prediction data.");

        return;
    }

    const labels = data.predictions.map(
        item => `Day ${item.day_offset}`
    );

    const values = data.predictions.map(
        item => item.predicted_temp
    );

    const canvas = document.getElementById("predictChart");

    const ctx = canvas.getContext("2d");

    if (predictChart) {

        predictChart.destroy();

    }

    predictChart = new Chart(ctx, {

        type: "line",

        data: {

            labels: labels,

            datasets: [

                {

                    label: "Predicted Temperature (°C)",

                    data: values,

                    borderColor: "#F2A65A",

                    backgroundColor: "rgba(242,166,90,0.2)",

                    fill: true,

                    tension: 0.4,

                    pointRadius: 5,

                    pointHoverRadius: 7

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            animation: true,

            plugins: {

                legend: {

                    labels: {

                        color: "#ffffff"

                    }

                }

            },

            scales: {

                x: {

                    ticks: {

                        color: "#ffffff"

                    },

                    grid: {

                        color: "#333"

                    }

                },

                y: {

                    ticks: {

                        color: "#ffffff"

                    },

                    grid: {

                        color: "#333"

                    }

                }

            }

        }

    });

}

async function loadRecommendations(city) {

    const data = await fetchJSON(
        `${API_BASE}/recommend?city=${encodeURIComponent(city)}`
    );

    els.recGrid.innerHTML = "";

    const sections = [

        {
            key: "clothing",
            title: "👕 Clothing"
        },

        {
            key: "activities",
            title: "🏃 Activities"
        },

        {
            key: "health",
            title: "❤️ Health"
        },

        {
            key: "travel",
            title: "✈️ Travel & Agriculture"
        }

    ];

    sections.forEach(section => {

        const card = document.createElement("div");

        card.className = "rec-card";

        card.innerHTML = `
            <div class="rec-title">${section.title}</div>
            <ul>
            ${(data.recommendations[section.key] || [])
                .map(item => `<li>${item}</li>`)
                .join("")}
            </ul>
        `;

        els.recGrid.appendChild(card);

    });

}

els.form.addEventListener("submit", async function (e) {

    e.preventDefault();

    const city = els.cityInput.value.trim();

    if (!city) return;

    try {

        await loadCurrent(city);

        await Promise.all([

            loadForecast(city),

            loadPrediction(city),

            loadRecommendations(city)

        ]);

    }

    catch (err) {

        console.error(err);

        showToast(err.message);

    }

});