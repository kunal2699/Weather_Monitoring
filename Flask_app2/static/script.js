// static/script.js
async function fetchWeather() {
    const response = await fetch('/api/weather');
    const data = await response.json();
    const weatherDataDiv = document.getElementById('weather-data');
    weatherDataDiv.innerHTML = ''; // Clear previous data

    data.forEach(cityData => {
        const cityDiv = document.createElement('div');
        cityDiv.innerHTML = `
            <h3>${cityData.city}</h3>
            <p>Temperature: ${cityData.temp.toFixed(2)} °C</p>
            <p>Feels Like: ${cityData.feels_like.toFixed(2)} °C</p>
            <p>Condition: ${cityData.condition}</p>
            <p>Time: ${new Date(cityData.timestamp).toLocaleString()}</p>
        `;
        weatherDataDiv.appendChild(cityDiv);
    });
}

// Fetch weather data at a configurable interval
setInterval(fetchWeather, 5 * 60 * 1000); // Every 5 minutes
fetchWeather(); // Initial fetch

// static/script.js
const ctx = document.getElementById('temperatureChart').getContext('2d');
let temperatureChart;

async function fetchDailySummaries() {
    const response = await fetch('/api/daily-summaries'); // Create this endpoint
    const summaries = await response.json();

    const labels = summaries.map(summary => summary.date);
    const averageTemps = summaries.map(summary => summary.average_temp);

    if (temperatureChart) {
        temperatureChart.destroy();
    }

    temperatureChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Temperature (°C)',
                data: averageTemps,
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                fill: false
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Call this function after fetching weather data
fetchDailySummaries();
