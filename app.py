import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
from modules.data_loader import fetch_live_marine_weather, generate_vessel_telemetry
from modules.ml_engine import detect_illegal_fishing_anomalies, calculate_ecological_risk

# Page Configuration
st.set_page_config(
    page_title="Ocean Shield Operations",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS: Plus Jakarta Sans, Dark Slate & Emerald Theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #090d16 !important;
        color: #f1f5f9;
    }

    .stApp {
        background-color: #090d16;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0d1322 !important;
        border-right: 1px solid #1e293b !important;
    }

    /* Metric Cards */
    .metric-card-highlight {
        background-color: #10b981;
        color: #090d16;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.2);
    }
    
    .metric-card-dark {
        background-color: #0d1322;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 20px;
    }

    .metric-title {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
    }

    .metric-title-light {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #090d16;
        opacity: 0.8;
    }

    .metric-value-dark {
        font-size: 2rem;
        font-weight: 800;
        color: #f8fafc;
        font-family: monospace;
        margin-top: 4px;
    }

    .metric-value-light {
        font-size: 2rem;
        font-weight: 800;
        color: #090d16;
        font-family: monospace;
        margin-top: 4px;
    }

    /* Badges */
    .badge-emerald {
        background-color: rgba(16, 185, 129, 0.1);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-family: monospace;
    }

    .badge-rose {
        background-color: rgba(225, 29, 72, 0.1);
        color: #fb7185;
        border: 1px solid rgba(225, 29, 72, 0.3);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-family: monospace;
    }

    /* Tabs Override */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0d1322;
        padding: 6px;
        border-radius: 8px;
        border: 1px solid #1e293b;
    }

    .stTabs [data-baseweb="tab"] {
        height: 36px;
        border-radius: 6px;
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background-color: #10b981 !important;
        color: #090d16 !important;
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Controls
st.sidebar.header("Control Center")

st.sidebar.subheader("Map Layer Visibility")
show_normal_vessels = st.sidebar.checkbox("Display Authorized Vessels", value=True, key="key_chk_normal")
show_suspicious_vessels = st.sidebar.checkbox("Display Suspicious Activity", value=True, key="key_chk_suspicious")
show_mpa_boundary = st.sidebar.checkbox("Display Protected Zone", value=True, key="key_chk_mpa")

st.sidebar.subheader("Filter Telemetry")
speed_filter = st.sidebar.slider("Max Vessel Speed (Knots)", 0.0, 20.0, 20.0, key="key_sld_speed")

# Header
st.title("Ocean Shield Operations")
st.caption("AI-Driven Maritime Intelligence & Ecological Risk Monitoring")

# Fetch Backend Data
weather = fetch_live_marine_weather()
vessels = generate_vessel_telemetry()
analyzed = detect_illegal_fishing_anomalies(vessels)
filtered_vessels = analyzed[analyzed['speed_knots'] <= speed_filter]
high_risk_count = len(filtered_vessels[filtered_vessels['risk_level'].str.contains('HIGH RISK')])

# Metrics Grid
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card-highlight">
        <div class="metric-title-light">Active Telemetry Units</div>
        <div class="metric-value-light">{len(filtered_vessels)}</div>
        <span style="font-size: 0.75rem; font-family: monospace;">100% Signal Coverage</span>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card-dark">
        <div class="metric-title">Sea Surface Temp</div>
        <div class="metric-value-dark">{weather['sst']} °C</div>
        <span class="badge-emerald">Open-Meteo Feed</span>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card-dark">
        <div class="metric-title">Wave Height</div>
        <div class="metric-value-dark">{weather['wave_height']} m</div>
        <span class="badge-emerald">Sea State Normal</span>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card-dark">
        <div class="metric-title">Flagged IUU Targets</div>
        <div class="metric-value-dark">{high_risk_count:02d}</div>
        <span class="badge-rose">Isolation Forest Flagged</span>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# Main Content Tabs
tab_map, tab_logs = st.tabs(["Operational Map", "Live Vessel Logs"])

with tab_map:
    st.subheader("Geospatial Monitor")
    m = folium.Map(location=[7.8, 80.7], zoom_start=7, tiles="CartoDB dark_matter")

    if show_mpa_boundary:
        folium.Rectangle(
            bounds=[[6.0, 80.0], [7.2, 81.5]],
            color="#10b981",
            weight=1.5,
            fill=True,
            fill_color="#10b981",
            fill_opacity=0.08,
            popup="Protected Marine Area"
        ).add_to(m)

    for _, row in filtered_vessels.iterrows():
        is_high_risk = "HIGH RISK" in row['risk_level']
        
        if (is_high_risk and show_suspicious_vessels) or (not is_high_risk and show_normal_vessels):
            color = "#fb7185" if is_high_risk else "#10b981"
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=7 if is_high_risk else 4,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.8,
                popup=f"Vessel: {row['vessel_id']} | Speed: {row['speed_knots']} kts"
            ).add_to(m)

    st_folium(m, width="100%", height=500)

with tab_logs:
    st.subheader("Live Vessel Logs")

    display_df = filtered_vessels[['vessel_id', 'speed_knots', 'dist_from_shore_nm', 'transponder_active', 'risk_level']].copy()
    display_df.columns = ['Vessel ID', 'Speed (kts)', 'Shore Distance (NM)', 'AIS Status', 'Risk Assessment']

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )