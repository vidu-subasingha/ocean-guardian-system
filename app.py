import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
from modules.data_loader import fetch_live_marine_weather, generate_vessel_telemetry
from modules.ml_engine import detect_illegal_fishing_anomalies, calculate_ecological_risk

# Page Configuration
st.set_page_config(
    page_title="Ocean Guardian System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Glassmorphism & Public Cards)
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .metric-card {
        background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        margin-bottom: 10px;
    }
    .metric-title { font-size: 0.85rem; color: #8b949e; text-transform: uppercase; font-weight: 600; }
    .metric-value { font-size: 1.5rem; color: #f0f6fc; font-weight: 700; margin-top: 4px; }
    .advisory-card {
        background-color: #161b22;
        border-left: 5px solid #58a6ff;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    .status-badge-high { background-color: #da3633; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
    .status-badge-mod { background-color: #d29922; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
    .status-badge-ok { background-color: #238636; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Main Application Header
st.title("🛡️ Ocean Guardian System")
st.caption("AI-Driven Maritime Intelligence & Ecological Risk Monitoring Platform | Team Ocean Shield")

# Load Backend Data
weather = fetch_live_marine_weather()
vessels = generate_vessel_telemetry()
analyzed_vessels = detect_illegal_fishing_anomalies(vessels)
bleaching_risk, algal_risk = calculate_ecological_risk(weather['sst'], weather['wave_height'])

high_risk_count = len(analyzed_vessels[analyzed_vessels['risk_level'].str.contains('HIGH RISK')])

# Sidebar Controls with Tooltips & Explanations
st.sidebar.header("🕹️ Control Center")
st.sidebar.info("💡 **How to use:** Toggle options below to filter vessels on the map or adjust viewing parameters.")

st.sidebar.subheader("Map Layer Visibility")
show_normal_vessels = st.sidebar.checkbox("Display Authorized Vessels", value=True, key="key_chk_normal")
show_suspicious_vessels = st.sidebar.checkbox("Display Suspicious Activity Alerts", value=True, key="key_chk_suspicious")
show_mpa_boundary = st.sidebar.checkbox("Display Protected Marine Zone", value=True, key="key_chk_mpa")

st.sidebar.subheader("Filter Telemetry")
speed_filter = st.sidebar.slider("Maximum Vessel Speed (Knots)", 0.0, 20.0, 20.0, key="key_sld_speed", help="1 Knot = ~1.85 km/h")
filtered_vessels = analyzed_vessels[analyzed_vessels['speed_knots'] <= speed_filter]

# Top KPI Cards
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Sea Surface Temp</div>
        <div class="metric-value">{weather['sst']} °C</div>
        <span class="status-badge-ok">Live Ocean Sensor</span>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Wave Height</div>
        <div class="metric-value">{weather['wave_height']} m</div>
        <span class="status-badge-ok">Normal Conditions</span>
    </div>
    """, unsafe_allow_html=True)

with c3:
    badge_class = "status-badge-mod" if "MODERATE" in bleaching_risk else ("status-badge-high" if "CRITICAL" in bleaching_risk else "status-badge-ok")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Coral Health Alert</div>
        <div class="metric-value" style="font-size: 1.1rem;">{bleaching_risk}</div>
        <span class="{badge_class}">Thermal Stress Indicator</span>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Suspicious Activity</div>
        <div class="metric-value">{high_risk_count} Alerts</div>
        <span class="status-badge-high">AI Flagged</span>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# Main Multi-Tab Display
tab_public, tab_map, tab_eco, tab_intel = st.tabs([
    "📢 Public Advisories & Simple Summary",
    "🗺️ Interactive Ocean Map", 
    "🌊 Ecological Hazard Analytics", 
    "🚨 Security & Illegal Fishing Intelligence"
])

# TAB 1: PUBLIC ADVISORIES & SIMPLE SUMMARY
with tab_public:
    st.subheader("Current Ocean Health & Safety Status")
    st.write("This overview provides easy-to-understand guidance for coastal communities, local fisheries, and maritime operators.")
    
    col_pub1, col_pub2 = st.columns(2)
    
    with col_pub1:
        st.markdown("""
        <div class="advisory-card">
            <h4>🚤 Coastal Fishery Guidance</h4>
            <p><b>Status: Safe for Fishing Operations</b></p>
            <p>Current wave heights and surface currents remain within standard operating limits. Small craft operations are cleared for coastal sectors.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="advisory-card">
            <h4>🪸 Coral Reef Ecosystem Watch</h4>
            <p><b>Status: Warm Water Watch Active</b></p>
            <p>Sea surface temperatures are hovering around normal seasonal highs. Coral reef monitoring groups are advised to conduct routine health surveys in shallow reefs.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_pub2:
        st.markdown("#### Simple Guide to Map Symbols")
        st.write("""
        * 🟢 **Green Circle:** Authorized ship or fishing vessel following regular speeds and sharing position telemetry.
        * 🔴 **Red Circle:** Vessel flagged for unusual behavior (such as turning off position signals or loitering near restricted waters).
        * 🟦 **Cyan Box:** Protected Marine Sanctuary where commercial fishing is strictly prohibited to preserve biodiversity.
        """)

# TAB 2: GEOSPATIAL MAP
with tab_map:
    st.subheader("Live Maritime Situational Awareness Map")
    
    m = folium.Map(location=[7.8, 80.7], zoom_start=7, tiles="CartoDB dark_matter")

    if show_mpa_boundary:
        folium.Rectangle(
            bounds=[[6.0, 80.0], [7.2, 81.5]],
            color="#00f2fe",
            weight=2,
            fill=True,
            fill_color="#00f2fe",
            fill_opacity=0.1,
            popup="Marine Protected Area (Restricted Area)"
        ).add_to(m)

    for _, row in filtered_vessels.iterrows():
        is_high_risk = "HIGH RISK" in row['risk_level']
        
        if (is_high_risk and show_suspicious_vessels) or (not is_high_risk and show_normal_vessels):
            color = "#ff4b4b" if is_high_risk else "#00c853"
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=8 if is_high_risk else 5,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.8,
                popup=f"<b>Vessel Identifier:</b> {row['vessel_id']}<br>"
                      f"<b>Speed:</b> {row['speed_knots']} knots<br>"
                      f"<b>Signal Status:</b> {'ACTIVE' if row['transponder_active'] else 'OFFLINE'}<br>"
                      f"<b>Assessment:</b> {row['risk_level']}"
            ).add_to(m)

    st_folium(m, width="100%", height=520)

# TAB 3: ECOLOGICAL ANALYTICS
with tab_eco:
    st.subheader("Marine Ecosystem Health & Environmental Stress")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### Sea Temperature Forecast vs Risk Threshold")
        dates = pd.date_range(end=pd.Timestamp.today(), periods=7)
        temp_data = pd.DataFrame({
            'Date': dates,
            'Temperature (°C)': [28.9, 29.1, 29.3, 29.5, 29.8, 30.1, 30.4]
        })
        fig_temp = px.line(temp_data, x='Date', y='Temperature (°C)', title="7-Day Sea Surface Temperature Forecast", markers=True)
        fig_temp.add_hline(y=30.0, line_dash="dash", line_color="red", annotation_text="Heat Stress Threshold")
        fig_temp.update_layout(template="plotly_dark")
        st.plotly_chart(fig_temp, use_container_width=True)

    with col_b:
        st.markdown("#### Water Conditions & Algal Bloom Risk")
        st.info(f"**Current Algal Bloom Risk:** {algal_risk}")
        st.write("""
        **What does this mean?**
        When ocean waters remain warm and sea swells are low, ocean mixing decreases. This can encourage rapid growth of microscopic algae (algal blooms).
        
        **Recommended Action:** Coastal authorities should regularly test water samples in shallow bays to ensure safety for local aquaculture.
        """)

# TAB 4: IUU INTELLIGENCE
with tab_intel:
    st.subheader("Machine Learning Anomaly Detection Logs")
    
    high_risk_df = filtered_vessels[filtered_vessels['risk_level'].str.contains("HIGH RISK")]
    
    if not high_risk_df.empty:
        st.warning(f"⚠️ {len(high_risk_df)} Vessels Currently Displaying Suspicious Navigation Patterns")
        
        # User-friendly column display
        display_df = high_risk_df[['vessel_id', 'latitude', 'longitude', 'speed_knots', 'transponder_active', 'dist_from_shore_nm', 'risk_level']].copy()
        display_df.columns = ['Vessel ID', 'Latitude', 'Longitude', 'Speed (Knots)', 'Signal Active', 'Distance Off Shore (Miles)', 'AI Risk Assessment']
        
        st.dataframe(display_df, use_container_width=True)
        
        fig_scatter = px.scatter(
            filtered_vessels, 
            x='dist_from_shore_nm', 
            y='speed_knots', 
            color='risk_level',
            title="Vessel Pattern Clustering (Speed vs. Distance from Shore)",
            labels={'dist_from_shore_nm': 'Distance Off Shore (Nautical Miles)', 'speed_knots': 'Speed (Knots)'},
            template="plotly_dark"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.success("No High-Risk Anomalies Detected within current filter parameters.")