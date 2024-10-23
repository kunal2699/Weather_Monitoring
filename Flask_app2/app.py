# app.py
from flask import Flask, render_template, jsonify
import requests
import datetime
import pymongo
import os

app = Flask(__name__)

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["weather_db"]
collection = db["daily_summaries"]

API_KEY = '9de788275f03a406e14ed188a983f67f'
CITIES = ["Delhi", "Mumbai", "Chennai", "Bangalore", "Kolkata", "Hyderabad"]

def fetch_weather_data():
    weather_data = []
    for city in CITIES:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            main = data['main']
            weather_data.append({
                'city': city,
                'temp': main['temp'] - 273.15,  # Convert from Kelvin to Celsius
                'feels_like': main['feels_like'] - 273.15,
                'condition': data['weather'][0]['main'],
                'timestamp': datetime.datetime.now()
            })
    return weather_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/weather')
def weather():
    data = fetch_weather_data()
    return jsonify(data)

# Add to app.py
def aggregate_weather_data(weather_data):
    for data in weather_data:
        date = data['timestamp'].date()
        summary = collection.find_one({'date': date})

        if not summary:
            summary = {
                'date': date,
                'average_temp': data['temp'],
                'max_temp': data['temp'],
                'min_temp': data['temp'],
                'dominant_condition': data['condition'],
                'count': 1
            }
            collection.insert_one(summary)
        else:
            summary['average_temp'] = ((summary['average_temp'] * summary['count']) + data['temp']) / (summary['count'] + 1)
            summary['max_temp'] = max(summary['max_temp'], data['temp'])
            summary['min_temp'] = min(summary['min_temp'], data['temp'])
            collection.update_one({'date': date}, {"$set": summary, "$inc": {"count": 1}})

def check_alerts(weather_data, thresholds):
    alerts = []
    for data in weather_data:
        if data['temp'] > thresholds['temperature']:
            alerts.append(f"Alert! {data['city']} exceeded {thresholds['temperature']} °C.")
    return alerts

@app.route('/api/daily-summaries')
def daily_summaries():
    summaries = list(collection.find({}, {'_id': 0}))  # Exclude MongoDB ID
    return jsonify(summaries)

if __name__ == '__main__':
    app.run(debug=True)
