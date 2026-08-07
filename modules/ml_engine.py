import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_illegal_fishing_anomalies(vessel_df):
    """
    Trains an Isolation Forest anomaly detection model to flag potential IUU fishing activities.
    """
    features = vessel_df[['speed_knots', 'transponder_active', 'dist_from_shore_nm']].copy()
    features['transponder_active'] = features['transponder_active'].astype(int)

    model = IsolationForest(contamination=0.18, random_state=42)
    vessel_df['anomaly_code'] = model.fit_predict(features)

    vessel_df['risk_level'] = np.where(
        (vessel_df['anomaly_code'] == -1) | (~vessel_df['transponder_active']),
        'HIGH RISK (Suspicious IUU Activity)',
        'Normal Operating Behavior'
    )
    return vessel_df

def calculate_ecological_risk(sst, wave_height):
    """
    Computes Coral Bleaching and Algal Bloom Risk metrics based on environmental thresholds.
    """
    # Convert None values safely
    sst_val = float(sst) if sst is not None else 29.5
    wave_val = float(wave_height) if wave_height is not None else 1.2

    # Baseline SST threshold for coral bleaching risk
    bleaching_risk = "LOW"
    if sst_val > 30.5:
        bleaching_risk = "CRITICAL (Severe Heat Stress)"
    elif sst_val > 29.5:
        bleaching_risk = "MODERATE (Watch Zone)"

    # Algal bloom indicator based on warm stagnant water conditions
    algal_risk = "LOW"
    if sst_val > 29.0 and wave_val < 0.8:
        algal_risk = "HIGH (Stagnant Warm Waters)"

    return bleaching_risk, algal_risk