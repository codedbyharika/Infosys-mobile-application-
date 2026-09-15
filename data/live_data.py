import requests
import random
from datetime import datetime

def fetch_live_weather(lat: float, lon: float) -> dict:
    """
    Fetches real-time weather from Open-Meteo (No API key required).
    """
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            temp = current.get("temperature_2m", 25.0)
            humidity = current.get("relative_humidity_2m", 50)
            wind_speed = current.get("wind_speed_10m", 5.0)
            wind_deg_val = current.get("wind_direction_10m", 0)
            
            # Convert wind degree to string representation
            dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
            ix = int((wind_deg_val + 11.25) / 22.5) % 16
            wind_deg_str = f"{dirs[ix]} ({wind_deg_val} deg)"
            
            weather_desc = "Clear"
            if humidity > 80: weather_desc = "Humid"
            if temp > 35: weather_desc = "Hot and Sunny"
            elif temp < 15: weather_desc = "Cool and Breezy"
            
            return {
                "temp": temp,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "wind_deg": wind_deg_str,
                "weather_desc": weather_desc
            }
    except Exception as e:
        print(f"Weather API error: {e}")
    
    # Fallback
    return {
        "temp": 28.5,
        "humidity": 60,
        "wind_speed": 10.2,
        "wind_deg": "NW (315 deg)",
        "weather_desc": "Data Unavailable (Fallback)"
    }


def fetch_live_aqi(lat: float, lon: float) -> dict:
    """
    Fetches real-time AQI from WAQI using the open feed endpoint.
    Falls back to simulated data if it fails.
    """
    try:
        # Using WAQI API (demo token for prototyping)
        url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token=demo"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                iaqi = data["data"].get("iaqi", {})
                aqi = data["data"].get("aqi", 50)
                
                if not isinstance(aqi, (int, float)):
                    aqi = 50
                    
                # WAQI provides PM2.5, PM10, etc., inside iaqi
                pm25 = float(iaqi.get("pm25", {}).get("v", 0.0))
                pm10 = float(iaqi.get("pm10", {}).get("v", 0.0))
                no2 = float(iaqi.get("no2", {}).get("v", 0.0))
                o3 = float(iaqi.get("o3", {}).get("v", 0.0))
                co = float(iaqi.get("co", {}).get("v", 0.0))
                so2 = float(iaqi.get("so2", {}).get("v", 0.0))
                
                # Determine dominant pollutant
                pollutants = {"PM2.5": pm25, "PM10": pm10, "NO2": no2, "O3": o3}
                dominant = max(pollutants, key=pollutants.get) if any(pollutants.values()) else "PM2.5"
                if not any(pollutants.values()):
                     pm25 = aqi * 0.4 # rough estimation if missing
                     pm10 = aqi * 0.8
                
                return {
                    "aqi": float(aqi),
                    "dominant_pollutant": dominant,
                    "pm25": pm25,
                    "pm10": pm10,
                    "no2": no2,
                    "o3": o3,
                    "co": co,
                    "so2": so2,
                    "stations": [
                         {"name": data["data"].get("city", {}).get("name", "Nearest Station"),
                          "lat": lat, "lon": lon, "aqi": aqi, "status": "Active"}
                    ]
                }
    except Exception as e:
        print(f"AQI API error: {e}")
        
    # Fallback to a mock location based on lat/lon
    return {
        "aqi": random.randint(40, 150),
        "dominant_pollutant": "PM2.5",
        "pm25": random.uniform(15.0, 75.0),
        "pm10": random.uniform(30.0, 120.0),
        "no2": random.uniform(10.0, 40.0),
        "o3": random.uniform(20.0, 50.0),
        "co": random.uniform(0.5, 2.0),
        "so2": random.uniform(5.0, 15.0),
        "stations": []
    }

def get_location_data(lat: float, lon: float) -> dict:
    """
    Combines live AQI and Weather into a single dictionary 
    compatible with the existing LOCATIONS_DATA format.
    """
    aqi_data = fetch_live_aqi(lat, lon)
    weather_data = fetch_live_weather(lat, lon)
    
    return {
        "city": "Current Location",
        "lat": lat,
        "lon": lon,
        "aqi": aqi_data["aqi"],
        "category": "Unknown", # Calculated later in UI using get_aqi_category_info
        "dominant_pollutant": aqi_data["dominant_pollutant"],
        "pm25": aqi_data["pm25"],
        "pm10": aqi_data["pm10"],
        "no2": aqi_data["no2"],
        "o3": aqi_data["o3"],
        "co": aqi_data["co"],
        "so2": aqi_data["so2"],
        "temp": weather_data["temp"],
        "humidity": weather_data["humidity"],
        "wind_speed": weather_data["wind_speed"],
        "wind_deg": weather_data["wind_deg"],
        "weather_desc": weather_data["weather_desc"],
        "stations": aqi_data["stations"]
    }
