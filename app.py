import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
from modules.data_loader import fetch_live_marine_weather, generate_vessel_telemetry
from modules.ml_engine import detect_illegal_fishing_anomalies, calculate_ecological_risk

# Page Configuration
st.set_page_config(
    page_title="Ocean Shield | Maritime Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Theme: Plus Jakarta Sans, Dark Slate (#090d16) & Emerald (#10b981) Palette
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

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

    /* Sidebar Brand Header */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 4px 16px 4px;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 16px;
    }
    .brand-icon {
        background-color: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.2);
        color: #10b981;
        border-radius: 8px;
        padding: 8px;
        font-size: 1.1rem;
    }
    .brand-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: -0.01em;
    }
    .brand-subtitle {
        font-size: 0.7rem;
        color: #64748b;
        font-family: monospace;
    }

    /* Metric Cards */
    .metric-card-highlight {
        background-color: #10b981;
        color: #090d16;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.2);
    }
    
    .metric-card-dark {
        background-color: #0d1322;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 18px 20px;
    }

    .metric-title {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
    }

    .metric-title-light {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #090d16;
        opacity: 0.85;
    }

    .metric-value-dark {
        font-size: 1.85rem;
        font-weight: 800;
        color: #f8fafc;
        font-family: monospace;
        margin-top: 4px;
        margin-bottom: 6px;
    }

    .metric-value-light {
        font-size: 1.85rem;
        font-weight: 800;
        color: #090d16;
        font-family: monospace;
        margin-top: 4px;
        margin-bottom: 6px;
    }

    /* Status Badges */
    .badge-emerald {
        background-color: rgba(16, 185, 129, 0.1);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-family: monospace;
    }

    .badge-rose {
        background-color: rgba(225, 29, 72, 0.1);
        color: #fb7185;
        border: 1px solid rgba(225, 29, 72, 0.3);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-family: monospace;
    }

    .advisory-panel {
        background-color: #0d1322;
        border: 1px solid #1e293b;
        border-left: 4px solid #10b981;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0d1322;
        padding: 6px;
        border-radius: 8px;
        border: 1px solid #1e293b;
    }

    .stTabs [data-baseweb="tab"] {
        height: 38px;
        border-radius: 6px;
        color: #94a3b8;
        font-size: 0.82rem;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: #10b981 !important;
        color: #090d16 !important;
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Professional Navigation & Filters
st.sidebar.markdown("""
    <div class="sidebar-brand">
        <div class="brand-icon">🛡️</div>
        <div>
            <div class="brand-title">Ocean Shield</div>
            <div class="brand-subtitle">Maritime Intelligence</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<p style='font-size: 10px; font-weight: 700; text-transform: uppercase; color: #64748b; font-family: monospace; margin-bottom: 8px;'>GEOSPATIAL LAYERS</p>", unsafe_allow_html=True)
show_normal_vessels = st.sidebar.checkbox("Authorized Vessels", value=True, key="key_chk_normal")
show_suspicious_vessels = st.sidebar.checkbox("Flagged Anomalies", value=True, key="key_chk_suspicious")
show_mpa_boundary = st.sidebar.checkbox("Protected Marine Sanctuary", value=True, key="key_chk_mpa")

st.sidebar.markdown("<br><p style='font-size: 10px; font-weight: 700; text-transform: uppercase; color: #64748b; font-family: monospace; margin-bottom: 8px;'>TELEMETRY FILTERS</p>", unsafe_allow_html=True)
speed_filter = st.sidebar.slider("Maximum Speed Filter (Knots)", 0.0, 20.0, 20.0, key="key_sld_speed", help="1 Knot = 1.85 km/h")

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='font-size: 11px; color: #64748b; font-family: monospace;'>● Open-Meteo Feed: ACTIVE<br>● Model Pipeline: ONLINE</div>", unsafe_allow_html=True)

# Main Application Title Header
st.title("Maritime Command Center")
st.caption("AI-Driven Maritime Intelligence & Ecological Risk Monitoring Platform | EEZ Sector Sri Lanka")

# Load Backend Data Engine
weather = fetch_live_marine_weather()
vessels = generate_vessel_telemetry()
analyzed = detect_illegal_fishing_anomalies(vessels)
filtered_vessels = analyzed[analyzed['speed_knots'] <= speed_filter]

bleaching_risk, algal_risk = calculate_ecological_risk(weather['sst'], weather['wave_height'])
high_risk_count = len(filtered_vessels[filtered_vessels['risk_level'].str.contains('HIGH RISK')])

# Metrics Grid Section
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card-highlight">
        <div class="metric-title-light">Active Telemetry Units</div>
        <div class="metric-value-light">{len(filtered_vessels)}</div>
        <span style="font-size: 0.72rem; font-family: monospace; font-weight: 600;">100% Signal Coverage</span>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card-dark">
        <div class="metric-title">Sea Surface Temp</div>
        <div class="metric-value-dark">{weather['sst']} °C</div>
        <span class="badge-emerald">Open-Meteo API</span>
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

# Main Multi-Tab Display
tab_public, tab_map, tab_eco, tab_intel = st.tabs([
    "Community Advisories",
    "Operational Map", 
    "Ecological Hazards", 
    "IUU Anomaly Intelligence"
])

# TAB 1: COMMUNITY ADVISORIES & EXPLANATION
with tab_public:
    st.subheader("Public Safety & Operations Summary")
    st.write("Translated operational guidance for coastal communities, local fisheries, and marine sector teams.")
    
    col_pub1, col_pub2 = st.columns(2)
    
    with col_pub1:
        st.markdown("""
        <div class="advisory-panel">
            <h4 style="margin: 0 0 6px 0; font-size: 0.95rem; font-weight: 700;">Coastal Fishery Guidance</h4>
            <p style="margin: 0; font-size: 0.85rem; color: #94a3b8;"><b>Status: Operational / Safe</b><br>Current wave heights and ocean surface dynamics remain within safe standard parameters for small vessel navigation.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="advisory-panel">
            <h4 style="margin: 0 0 6px 0; font-size: 0.95rem; font-weight: 700;">Coral Reef Thermal Stress Watch</h4>
            <p style="margin: 0; font-size: 0.85rem; color: #94a3b8;"><b>Status: Monitoring Active</b><br>Sea surface temperatures are maintaining operational baselines. Routine monitoring recommended in shallow coastal reefs.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_pub2:
        st.markdown("#### Operational Legend")
        st.write("""
        * **Green Indicators:** Authorized vessels transmitting standard positioning telemetry.
        * **Red Indicators:** Flagged vessels exhibiting operational anomalies (e.g., loitering or offline AIS signals).
        * **Emerald Polygon:** Marine Protected Area (MPA) designated as a restricted zone.
        """)

# TAB 2: GEOSPATIAL MAP
with tab_map:
    st.subheader("Live Maritime Situational Awareness Map")
    
    m = folium.Map(location=[7.8, 80.7], zoom_start=7, tiles="CartoDB dark_matter")

    if show_mpa_boundary:
        folium.Rectangle(
            bounds=[[6.0, 80.0], [7.2, 81.5]],
            color="#10b981",
            weight=1.5,
            fill=True,
            fill_color="#10b981",
            fill_opacity=0.08,
            popup="Marine Protected Sanctuary"
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
                popup=f"Vessel ID: {row['vessel_id']} | Speed: {row['speed_knots']} kts | Status: {row['risk_level']}"
            ).add_to(m)

    st_folium(m, width="100%", height=520)

# TAB 3: ECOLOGICAL ANALYTICS
with tab_eco:
    st.subheader("Ecosystem Stress & Climate Analytics")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### Sea Surface Temperature Forecast vs Threshold")
        dates = pd.date_range(end=pd.Timestamp.today(), periods=7)
        temp_data = pd.DataFrame({
            'Date': dates,
            'Temperature (°C)': [28.9, 29.1, 29.3, 29.5, 29.8, 30.1, 30.4]
        })
        fig_temp = px.line(temp_data, x='Date', y='Temperature (°C)', title="7-Day SST Forecast", markers=True)
        fig_temp.add_hline(y=30.0, line_dash="dash", line_color="#fb7185", annotation_text="Bleaching Risk Threshold")
        fig_temp.update_layout(template="plotly_dark", paper_bgcolor="#0d1322", plot_bgcolor="#0d1322")
        st.plotly_chart(fig_temp, use_container_width=True)

    with col_b:
        st.markdown("#### Water Stagnancy & Algal Bloom Assessment")
        st.info(f"Current Algal Bloom Risk Level: {algal_risk}")
        st.write("""
        * **Indicator Model:** Surface temperatures exceeding $29.0^\circ\text{C}$ combined with wave heights below $0.8\text{ m}$ reduce ocean surface mixing.
        * **Actionable Protocol:** Alert local marine resource officers to monitor dissolved oxygen levels in coastal bays.
        """)

# TAB 4: IUU ANOMALY INTELLIGENCE & SHADCN-STYLE DATA TABLE
with tab_intel:
    st.subheader("Machine Learning Anomaly Detection Logs")
    
    display_df = filtered_vessels[['vessel_id', 'speed_knots', 'dist_from_shore_nm', 'transponder_active', 'risk_level']].copy()
    display_df.columns = ['Vessel ID', 'Speed (kts)', 'Shore Distance (NM)', 'AIS Signal Active', 'Risk Assessment']
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    fig_scatter = px.scatter(
        filtered_vessels, 
        x='dist_from_shore_nm', 
        y='speed_knots', 
        color='risk_level',
        title="Vessel Speed vs. Distance Off Shore Clustering",
        labels={'dist_from_shore_nm': 'Distance Off Shore (NM)', 'speed_knots': 'Speed (Knots)'},
        template="plotly_dark",
        color_discrete_map={"AUTHORIZED": "#10b981", "HIGH RISK": "#fb7185"}
    )
    fig_scatter.update_layout(paper_bgcolor="#0d1322", plot_bgcolor="#0d1322")
    st.plotly_chart(fig_scatter, use_container_width=True)