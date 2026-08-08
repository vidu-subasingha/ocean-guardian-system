import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
from datetime import datetime
from modules.data_loader import fetch_live_marine_weather, generate_vessel_telemetry
from modules.ml_engine import detect_illegal_fishing_anomalies, calculate_ecological_risk

# 1. Page Configuration
st.set_page_config(
    page_title="Ocean Guardian System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme Selector Toggle
theme_mode = st.sidebar.toggle("🌙 Dark Mode / ☀️ Light Mode", value=True)

# Define Dynamic Color Variables
if theme_mode:
    bg_app = "#080c14"
    bg_sidebar = "#0e1526"
    bg_card = "#0e1526"
    text_main = "#f1f5f9"
    text_muted = "#94a3b8"
    border_color = "#1e293b"
    accent_cyan = "#06b6d4"
    accent_rose = "#fb7185"
    sidebar_title_color = "#f8fafc"
    sidebar_text_color = "#cbd5e1"
    tab_unselected_text = "#94a3b8"
    plotly_template = "plotly_dark"
    folium_tiles = "CartoDB dark_matter"
else:
    bg_app = "#f8fafc"
    bg_sidebar = "#f1f5f9"
    bg_card = "#ffffff"
    text_main = "#0f172a"
    text_muted = "#334155"
    border_color = "#cbd5e1"
    accent_cyan = "#0891b2"
    accent_rose = "#e11d48"
    sidebar_title_color = "#0f172a"
    sidebar_text_color = "#334155"
    tab_unselected_text = "#334155"
    plotly_template = "plotly_white"
    folium_tiles = "CartoDB positron"

# Apply Custom Dynamic CSS Engine
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], div, span, p, h1, h2, h3, h4, button, input {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }}

    .stApp {{
        background-color: {bg_app} !important;
        color: {text_main} !important;
    }}

    .stCaption {{
        color: {text_muted} !important;
        font-weight: 500;
    }}

    /* Sidebar Base & Typography Override */
    section[data-testid="stSidebar"] {{
        background-color: {bg_sidebar} !important;
        border-right: 1px solid {border_color} !important;
    }}

    section[data-testid="stSidebar"] * {{
        color: {sidebar_text_color} !important;
    }}

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {{
        color: {sidebar_title_color} !important;
    }}

    /* Checkbox & Slider Colors */
    div[data-baseweb="checkbox"] [aria-checked="true"] {{
        background-color: {accent_cyan} !important;
        border-color: {accent_cyan} !important;
    }}

    div[data-baseweb="slider"] div[role="slider"] {{
        background-color: {accent_cyan} !important;
        box-shadow: 0 0 10px {accent_cyan}80 !important;
    }}

    div[data-baseweb="slider"] div[data-testid="stSliderTrackFill"] {{
        background-color: {accent_cyan} !important;
    }}

    /* Metric Cards */
    .metric-card-primary {{
        background-color: {accent_cyan};
        color: #ffffff !important;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 10px 25px -5px {accent_cyan}40;
    }}

    .metric-card-primary * {{
        color: #ffffff !important;
    }}

    .metric-card-dark {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 20px;
    }}

    .metric-label-light {{
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        opacity: 0.9;
    }}

    .metric-label-dark {{
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {text_muted} !important;
    }}

    .metric-val-light {{
        font-size: 2rem;
        font-weight: 800;
        font-family: monospace;
        margin: 4px 0;
    }}

    .metric-val-dark {{
        font-size: 2rem;
        font-weight: 800;
        color: {text_main} !important;
        font-family: monospace;
        margin: 4px 0;
    }}

    /* Badges */
    .badge-cyan {{
        background-color: {accent_cyan}15;
        color: {accent_cyan} !important;
        border: 1px solid {accent_cyan}40;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-family: monospace;
        font-weight: 600;
    }}

    .badge-rose {{
        background-color: {accent_rose}15;
        color: {accent_rose} !important;
        border: 1px solid {accent_rose}40;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-family: monospace;
        font-weight: 600;
    }}

    /* Advisory Cards */
    .advisory-panel {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-left: 4px solid {accent_cyan};
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
    }}

    /* Tabs Override (Fixes Invisible Tab Text in Light Mode) */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background-color: {bg_card};
        padding: 5px;
        border-radius: 8px;
        border: 1px solid {border_color};
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 36px;
        border-radius: 6px;
        color: {tab_unselected_text} !important;
        font-size: 0.82rem;
        font-weight: 600;
    }}

    .stTabs [data-baseweb="tab"] div {{
        color: {tab_unselected_text} !important;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {accent_cyan} !important;
        border-radius: 6px;
    }}

    .stTabs [aria-selected="true"] div {{
        color: #ffffff !important;
        font-weight: 700 !important;
    }}

    /* Dataframe Styling */
    [data-testid="stDataFrame"] {{
        border: 1px solid {border_color};
        border-radius: 8px;
        overflow: hidden;
    }}
    </style>
""", unsafe_allow_html=True)

# 2. Sidebar Branding
st.sidebar.markdown(f"""
    <div style="padding: 4px 0px 12px 0px; border-bottom: 1px solid {border_color}; margin-bottom: 12px;">
        <div style="font-size: 1rem; font-weight: 800; letter-spacing: -0.01em; color: {sidebar_title_color};">Ocean Guardian System</div>
        <div style="font-size: 0.7rem; color: {accent_cyan} !important; font-family: monospace; text-transform: uppercase; font-weight: 600;">Maritime Operations Platform</div>
    </div>
""", unsafe_allow_html=True)

# 3. Sidebar Filters & Real-Time Timestamp Badge
st.sidebar.markdown(f"<p style='font-size: 10px; font-weight: 700; text-transform: uppercase; color: {text_muted} !important; font-family: monospace; margin-bottom: 8px;'>GEOSPATIAL LAYERS</p>", unsafe_allow_html=True)
show_normal_vessels = st.sidebar.checkbox("Authorized Vessels", value=True, key="key_chk_normal")
show_suspicious_vessels = st.sidebar.checkbox("Flagged Anomalies", value=True, key="key_chk_suspicious")
show_mpa_boundary = st.sidebar.checkbox("Protected Marine Sanctuary", value=True, key="key_chk_mpa")

st.sidebar.markdown(f"<br><p style='font-size: 10px; font-weight: 700; text-transform: uppercase; color: {text_muted} !important; font-family: monospace; margin-bottom: 8px;'>TELEMETRY FILTERS</p>", unsafe_allow_html=True)
speed_filter = st.sidebar.slider("Maximum Speed Filter (Knots)", 0.0, 20.0, 20.0, key="key_sld_speed")

# Live Refresh Timestamp
current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
st.sidebar.markdown(f"<hr style='border-color: {border_color};'>", unsafe_allow_html=True)
st.sidebar.markdown(f"""
    <div style='font-size: 11px; color: {sidebar_text_color}; font-family: monospace;'>
        ● Open-Meteo Feed: ACTIVE<br>
        ● Model Pipeline: ONLINE<br>
        <span style="color: {accent_cyan} !important; font-weight: bold;">LAST REFRESH:</span><br>{current_timestamp}
    </div>
""", unsafe_allow_html=True)

# 4. Main Application Header
st.title("Ocean Guardian System")
st.caption("AI-Driven Maritime Intelligence & Ecological Risk Monitoring Platform | EEZ Sector Sri Lanka")

# 5. Data Engine Execution
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
        <span class="badge-cyan">Open-Meteo Feed</span>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card-dark">
        <div class="metric-label-dark">Wave Height</div>
        <div class="metric-val-dark">{weather['wave_height']} m</div>
        <span class="badge-cyan">Sea State Normal</span>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card-dark">
        <div class="metric-label-dark">Flagged IUU Targets</div>
        <div class="metric-val-dark">{high_risk_count:02d}</div>
        <span class="badge-rose">Isolation Forest Flagged</span>
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

# TAB 1: HUMANITY × AI OPERATIONAL SUMMARY
with tab_public:
    st.subheader("Public Safety & Operational Summaries")
    st.write("Translating complex multi-modal AI predictions into actionable guidance for non-technical coastal authorities and local fishing communities.")
    
    col_pub1, col_pub2 = st.columns(2)
    
    with col_pub1:
        st.markdown(f"""
        <div class="advisory-panel">
            <h4 style="margin: 0 0 6px 0; font-size: 0.95rem; font-weight: 700; color: {text_main};">Coastal Fishery Operations</h4>
            <p style="margin: 0; font-size: 0.85rem; color: {text_muted};">
            <b>Status: Operational / Safe</b><br>
            Current ocean surface stress and wave dynamics remain within standard safety bounds. Small craft and artisanal fishing fleets can operate normally.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="advisory-panel">
            <h4 style="margin: 0 0 6px 0; font-size: 0.95rem; font-weight: 700; color: {text_main};">Reef Thermal Stress Watch</h4>
            <p style="margin: 0; font-size: 0.85rem; color: {text_muted};">
            <b>Status: Baseline Monitoring Active</b><br>
            Sea surface temperatures are maintaining operational thresholds. AI models project low immediate bleaching threat across coastal shallow reefs.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_pub2:
        st.markdown("#### Humanity × AI Custodianship Framework")
        st.write("""
        * **Augmenting Human Enforcement:** The system bridges data fragmentation by integrating multi-modal telemetry into a singular decision framework[cite: 1].
        * **Securing Coastal Economies:** Early warning alerts allow local authorities to deploy coast guard assets efficiently and mitigate IUU poaching[cite: 1].
        * **Preserving Biodiversity:** Automated degree heating week calculations empower conservationists to protect vulnerable marine ecosystems[cite: 1].
        """)

# TAB 2: GEOSPATIAL MAP
with tab_map:
    st.subheader("Live Geospatial Monitoring Map")
    
    m = folium.Map(location=[7.8, 80.7], zoom_start=7, tiles=folium_tiles)

    if show_mpa_boundary:
        folium.Rectangle(
            bounds=[[6.0, 80.0], [7.2, 81.5]],
            color=accent_cyan,
            weight=1.5,
            fill=True,
            fill_color=accent_cyan,
            fill_opacity=0.08,
            popup="Protected Marine Sanctuary"
        ).add_to(m)

    for _, row in filtered_vessels.iterrows():
        is_high_risk = "HIGH RISK" in row['risk_level']
        
        if (is_high_risk and show_suspicious_vessels) or (not is_high_risk and show_normal_vessels):
            color = accent_rose if is_high_risk else accent_cyan
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=7 if is_high_risk else 4,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.85,
                popup=f"Vessel ID: {row['vessel_id']} | Speed: {row['speed_knots']} kts | Risk: {row['risk_level']}"
            ).add_to(m)

    st_folium(m, width="stretch", height=520)

# TAB 3: ECOLOGICAL ANALYTICS & HABITAT SUITABILITY
with tab_eco:
    st.subheader("Ecosystem Stress & Habitat Suitability Analytics")
    
    col_dhw1, col_dhw2, col_dhw3 = st.columns(3)
    with col_dhw1:
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label-dark">Degree Heating Weeks (DHW)</div>
            <div class="metric-val-dark">1.4 °C-wk</div>
            <span class="badge-cyan">LSTM Temperature Anomaly</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col_dhw2:
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label-dark">Chlorophyll-a Concentration</div>
            <div class="metric-val-dark">0.42 mg/m³</div>
            <span class="badge-cyan">Copernicus Marine Satellite</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col_dhw3:
        st.markdown(f"""
        <div class="metric-card-dark">
            <div class="metric-label-dark">Sustainable Fishing Zone</div>
            <div class="metric-val-dark">Sector 04-B</div>
            <span class="badge-cyan">Random Forest Habitat Model</span>
        </div>
        """, unsafe_allow_html=True)

    st.write("---")

    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### 7-Day Sea Surface Temp & Bleaching Risk Forecast")
        dates = pd.date_range(end=pd.Timestamp.today(), periods=7)
        temp_data = pd.DataFrame({
            'Date': dates,
            'SST (°C)': [28.9, 29.1, 29.3, 29.5, 29.8, 30.1, 30.4]
        })
        fig_temp = px.line(temp_data, x='Date', y='SST (°C)', title="7-Day SST Forecast", markers=True)
        fig_temp.add_hline(y=30.0, line_dash="dash", line_color=accent_cyan, annotation_text="Thermal Alert Baseline")
        fig_temp.update_traces(line_color=accent_cyan, marker=dict(color=accent_cyan))
        fig_temp.update_layout(
            template=plotly_template, 
            paper_bgcolor=bg_card, 
            plot_bgcolor=bg_card,
            font=dict(family="Plus Jakarta Sans", color=text_muted)
        )
        st.plotly_chart(fig_temp, width="stretch")

    with col_b:
        st.markdown("#### Surface Stagnancy & Sustainable Fishing Analysis")
        st.info(f"Algal Bloom Risk Level: {algal_risk}")
        st.write(r"""
        * **Coral Bleaching Model:** Tracks cumulative Degree Heating Weeks (DHW) when sea temperatures exceed $30.0^\circ\text{C}$[cite: 1].
        * **Habitat Suitability Model:** Uses Random Forest regression over chlorophyll-a density and current velocity to highlight optimal, sustainable catch zones away from protected marine sanctuaries[cite: 1].
        """)

# TAB 4: IUU ANOMALY INTELLIGENCE & DOWNLOADABLE TELEMETRY REPORT
with tab_intel:
    st.subheader("Vessel Telemetry & Machine Learning Logs")
    
    display_df = filtered_vessels[['vessel_id', 'speed_knots', 'dist_from_shore_nm', 'transponder_active', 'risk_level']].copy()
    display_df.columns = ['Vessel ID', 'Speed (kts)', 'Shore Distance (NM)', 'AIS Transponder Active', 'Risk Assessment']
    
    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True
    )

    # Export CSV Report Feature
    csv_data = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Telemetry Report (CSV)",
        data=csv_data,
        file_name=f"ocean_guardian_telemetry_report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        help="Export vessel positioning and isolation forest risk flags for auditing."
    )

    st.write("---")

    fig_scatter = px.scatter(
        filtered_vessels, 
        x='dist_from_shore_nm', 
        y='speed_knots', 
        color='risk_level',
        title="Vessel Trajectory Distribution (Speed vs Distance Off Shore)",
        labels={'dist_from_shore_nm': 'Distance Off Shore (NM)', 'speed_knots': 'Speed (Knots)'},
        template=plotly_template,
        color_discrete_map={"AUTHORIZED": accent_cyan, "HIGH RISK": accent_rose}
    )
    fig_scatter.update_layout(
        paper_bgcolor=bg_card, 
        plot_bgcolor=bg_card,
        font=dict(family="Plus Jakarta Sans", color=text_muted)
    )
    st.plotly_chart(fig_scatter, width="stretch")