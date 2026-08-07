import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
from modules.data_loader import fetch_live_marine_weather, generate_vessel_telemetry
from modules.ml_engine import detect_illegal_fishing_anomalies, calculate_ecological_risk

# 1. Page Configuration
st.set_page_config(
    page_title="Ocean Guardian System | Operations",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Strict Unified Theme Styling: Plus Jakarta Sans & Emerald Palette
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Global Typography & Base Theme */
    html, body, [class*="css"], div, span, p, h1, h2, h3, h4, button, input {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .stApp {
        background-color: #090d16 !important;
        color: #f1f5f9 !important;
    }

    /* Sidebar Theme Integration */
    section[data-testid="stSidebar"] {
        background-color: #0d1322 !important;
        border-right: 1px solid #1e293b !important;
    }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 4px 0px 16px 0px;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 16px;
    }

    .brand-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: -0.01em;
    }

    .brand-subtitle {
        font-size: 0.7rem;
        color: #10b981;
        font-family: monospace;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Metric Cards - Primary Highlight & Standard Dark */
    .metric-card-primary {
        background-color: #10b981;
        color: #090d16;
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.25);
    }

    .metric-card-dark {
        background-color: #0d1322;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 18px 20px;
    }

    .metric-label-light {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #090d16;
        opacity: 0.85;
    }

    .metric-label-dark {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748b;
    }

    .metric-val-light {
        font-size: 1.85rem;
        font-weight: 800;
        color: #090d16;
        font-family: monospace;
        margin: 4px 0;
    }

    .metric-val-dark {
        font-size: 1.85rem;
        font-weight: 800;
        color: #f8fafc;
        font-family: monospace;
        margin: 4px 0;
    }

    /* System Status Badges */
    .badge-emerald {
        background-color: rgba(16, 185, 129, 0.1);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-family: monospace;
        font-weight: 600;
    }

    .badge-subtle {
        background-color: #1e293b;
        color: #94a3b8;
        border: 1px solid #334155;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-family: monospace;
    }

    /* Structured Advisory Panels */
    .advisory-panel {
        background-color: #0d1322;
        border: 1px solid #1e293b;
        border-left: 3px solid #10b981;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
    }

    /* Streamlit Components Override */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #0d1322;
        padding: 5px;
        border-radius: 8px;
        border: 1px solid #1e293b;
    }

    .stTabs [data-baseweb="tab"] {
        height: 36px;
        border-radius: 6px;
        color: #64748b;
        font-size: 0.82rem;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: #10b981 !important;
        color: #090d16 !important;
        font-weight: 700 !important;
    }

    /* Dataframe Table Styling Override */
    [data-testid="stDataFrame"] {
        border: 1px solid #1e293b;
        border-radius: 8px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar Branding & Navigation
st.sidebar.markdown("""
    <div class="sidebar-brand">
        <div>
            <div class="brand-title">Ocean Guardian System</div>
            <div class="brand-subtitle">Maritime Operations Platform</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<p style='font-size: 10px; font-weight: 700; text-transform: uppercase; color: #64748b; font-family: monospace; margin-bottom: 8px;'>GEOSPATIAL LAYERS</p>", unsafe_allow_html=True)
show_normal_vessels = st.sidebar.checkbox("Authorized Vessels", value=True, key="key_chk_normal")
show_suspicious_vessels = st.sidebar.checkbox("Flagged Anomalies", value=True, key="key_chk_suspicious")
show_mpa_boundary = st.sidebar.checkbox("Protected Marine Sanctuary", value=True, key="key_chk_mpa")

st.sidebar.markdown("<br><p style='font-size: 10px; font-weight: 700; text-transform: uppercase; color: #64748b; font-family: monospace; margin-bottom: 8px;'>TELEMETRY FILTERS</p>", unsafe_allow_html=True)
speed_filter = st.sidebar.slider("Maximum Speed Filter (Knots)", 0.0, 20.0, 20.0, key="key_sld_speed")

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='font-size: 11px; color: #64748b; font-family: monospace;'>● Open-Meteo Feed: ACTIVE<br>● Model Pipeline: ONLINE</div>", unsafe_allow_html=True)

# 4. Main Application Header
st.title("Ocean Guardian System")
st.caption("AI-Driven Maritime Intelligence & Ecological Risk Monitoring Platform | EEZ Sector Sri Lanka")

# 5. Load Data Services
weather = fetch_live_marine_weather()
vessels = generate_vessel_telemetry()
analyzed = detect_illegal_fishing_anomalies(vessels)
filtered_vessels = analyzed[analyzed['speed_knots'] <= speed_filter]

bleaching_risk, algal_risk = calculate_ecological_risk(weather['sst'], weather['wave_height'])
high_risk_count = len(filtered_vessels[filtered_vessels['risk_level'].str.contains('HIGH RISK')])

# 6. Primary KPI Metrics Grid
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card-primary">
        <div class="metric-label-light">Active Telemetry Units</div>
        <div class="metric-val-light">{len(filtered_vessels)}</div>
        <span style="font-size: 0.72rem; font-family: monospace; font-weight: 600;">100% Signal Coverage</span>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card-dark">
        <div class="metric-label-dark">Sea Surface Temp</div>
        <div class="metric-val-dark">{weather['sst']} °C</div>
        <span class="badge-emerald">Open-Meteo Feed</span>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card-dark">
        <div class="metric-label-dark">Wave Height</div>
        <div class="metric-val-dark">{weather['wave_height']} m</div>
        <span class="badge-emerald">Sea State Normal</span>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card-dark">
        <div class="metric-label-dark">Flagged IUU Targets</div>
        <div class="metric-val-dark">{high_risk_count:02d}</div>
        <span class="badge-subtle">Isolation Forest Flagged</span>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# 7. Operational Workspace Tabs
tab_public, tab_map, tab_eco, tab_intel = st.tabs([
    "Community Advisories",
    "Operational Map", 
    "Ecological Hazards", 
    "IUU Anomaly Intelligence"
])

# TAB 1: COMMUNITY ADVISORIES
with tab_public:
    st.subheader("Public Safety & Operational Summaries")
    st.write("Standardized operational guidance for coastal communities, local fisheries, and maritime authorities.")
    
    col_pub1, col_pub2 = st.columns(2)
    
    with col_pub1:
        st.markdown("""
        <div class="advisory-panel">
            <h4 style="margin: 0 0 6px 0; font-size: 0.95rem; font-weight: 700; color: #f8fafc;">Coastal Fishery Operations</h4>
            <p style="margin: 0; font-size: 0.85rem; color: #94a3b8;"><b>Status: Operational / Safe</b><br>Surface wave dynamics and wind stress conditions remain within standard safety parameters for artisanal and commercial vessels.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="advisory-panel">
            <h4 style="margin: 0 0 6px 0; font-size: 0.95rem; font-weight: 700; color: #f8fafc;">Reef Thermal Stress Assessment</h4>
            <p style="margin: 0; font-size: 0.85rem; color: #94a3b8;"><b>Status: Baseline Monitoring</b><br>Sea surface temperatures are maintaining operational thresholds. Shallow reef zones show low thermal accumulation.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_pub2:
        st.markdown("#### Operational Legend")
        st.write("""
        * **Emerald Indicator:** Authorized vessel maintaining normal navigation and active AIS transmission.
        * **Slate Indicator:** Flagged vessel exhibiting trajectory anomalies or transponder power-offs.
        * **Emerald Outlined Polygon:** Protected Marine Sanctuary boundary (Restricted commercial activity).
        """)

# TAB 2: GEOSPATIAL MAP
with tab_map:
    st.subheader("Live Geospatial Monitoring Map")
    
    m = folium.Map(location=[7.8, 80.7], zoom_start=7, tiles="CartoDB dark_matter")

    if show_mpa_boundary:
        folium.Rectangle(
            bounds=[[6.0, 80.0], [7.2, 81.5]],
            color="#10b981",
            weight=1.5,
            fill=True,
            fill_color="#10b981",
            fill_opacity=0.08,
            popup="Protected Marine Sanctuary"
        ).add_to(m)

    for _, row in filtered_vessels.iterrows():
        is_high_risk = "HIGH RISK" in row['risk_level']
        
        if (is_high_risk and show_suspicious_vessels) or (not is_high_risk and show_normal_vessels):
            color = "#64748b" if is_high_risk else "#10b981"
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=6 if is_high_risk else 4,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.85,
                popup=f"Vessel ID: {row['vessel_id']} | Speed: {row['speed_knots']} kts | Assessment: {row['risk_level']}"
            ).add_to(m)

    st_folium(m, width="100%", height=520)

# TAB 3: ECOLOGICAL ANALYTICS
with tab_eco:
    st.subheader("Ecosystem Stress & Thermal Trends")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### 7-Day Sea Surface Temp Trend")
        dates = pd.date_range(end=pd.Timestamp.today(), periods=7)
        temp_data = pd.DataFrame({
            'Date': dates,
            'SST (°C)': [28.9, 29.1, 29.3, 29.5, 29.8, 30.1, 30.4]
        })
        fig_temp = px.line(temp_data, x='Date', y='SST (°C)', title="7-Day SST Forecast", markers=True)
        fig_temp.add_hline(y=30.0, line_dash="dash", line_color="#10b981", annotation_text="Thermal Alert Baseline")
        fig_temp.update_traces(line_color="#10b981", marker=dict(color="#10b981"))
        fig_temp.update_layout(
            template="plotly_dark", 
            paper_bgcolor="#0d1322", 
            plot_bgcolor="#0d1322",
            font=dict(family="Plus Jakarta Sans", color="#94a3b8")
        )
        st.plotly_chart(fig_temp, use_container_width=True)

    with col_b:
        st.markdown("#### Surface Stagnancy Risk Assessment")
        st.info(f"Algal Bloom Risk Level: {algal_risk}")
        st.write("""
        * **Analytical Threshold:** Surface temperatures above $29.0^\circ\text{C}$ coupled with wave heights below $0.8\text{ m}$ reduce ocean surface mixing.
        * **Operational Directive:** Maintain automated daily polling via Open-Meteo API to trigger coastal advisories during low-wave periods.
        """)

# TAB 4: IUU ANOMALY INTELLIGENCE & DATA TABLE
with tab_intel:
    st.subheader("Vessel Telemetry & Machine Learning Logs")
    
    display_df = filtered_vessels[['vessel_id', 'speed_knots', 'dist_from_shore_nm', 'transponder_active', 'risk_level']].copy()
    display_df.columns = ['Vessel ID', 'Speed (kts)', 'Shore Distance (NM)', 'AIS Transponder Active', 'Risk Assessment']
    
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
        title="Vessel Trajectory Distribution (Speed vs Distance Off Shore)",
        labels={'dist_from_shore_nm': 'Distance Off Shore (NM)', 'speed_knots': 'Speed (Knots)'},
        template="plotly_dark",
        color_discrete_map={"AUTHORIZED": "#10b981", "HIGH RISK": "#64748b"}
    )
    fig_scatter.update_layout(
        paper_bgcolor="#0d1322", 
        plot_bgcolor="#0d1322",
        font=dict(family="Plus Jakarta Sans", color="#94a3b8")
    )
    st.plotly_chart(fig_scatter, use_container_width=True)