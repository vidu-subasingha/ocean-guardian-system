import pandas as pd
import numpy as np
import requests

def fetch_live_marine_weather(lat=7.5, lon=80.5):
    """
    Fetches real-time marine weather, sea surface temperature, and wave heights
    from the Open-Meteo Marine API with fallback defaults for missing values.
    """
    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&current=wave_height,sea_surface_temperature,ocean_current_velocity"
    try:
        response = requests.get(url, timeout=10)
        data = response.json().get('current', {})
        
        # Safely extract values and fallback to defaults if None
        sst = data.get('sea_surface_temperature')
        wave = data.get('wave_height')
        current = data.get('ocean_current_velocity')
        
        return {
            'sst': float(sst) if sst is not None else 29.5,
            'wave_height': float(wave) if wave is not None else 1.2,
            'current_velocity': float(current) if current is not None else 0.8
        }
    except Exception:
        return {'sst': 29.2, 'wave_height': 1.1, 'current_velocity': 0.7}

def generate_vessel_telemetry(num_vessels=30):
    """
    Generates synthetic AIS vessel telemetry data centered around Sri Lankan / Indian Ocean waters.
    """
    np.random.seed(42)
    lats = np.random.uniform(5.8, 9.8, num_vessels)
    lons = np.random.uniform(79.2, 82.2, num_vessels)
    
    speeds = np.random.choice([1.2, 1.8, 10.5, 12.0, 14.5], size=num_vessels)
    transponder_on = np.random.choice([True, False], p=[0.82, 0.18], size=num_vessels)
    dist_from_shore = np.random.uniform(5, 120, num_vessels)

    df = pd.DataFrame({
        'vessel_id': [f"MMSI_{241000 + i}" for i in range(num_vessels)],
        'latitude': lats,
        'longitude': lons,
        'speed_knots': speeds,
        'transponder_active': transponder_on,
        'dist_from_shore_nm': dist_from_shore
    })
    return df