# ============================================
# FILE: dashboard_testing.py (FINAL COMPLETE VERSION)
# INCLUDES ALL:
# - Analytics charts (Heatmap, High-risk, Police)
# - Hardware metrics (CPU, RAM, Time)
# - Scheduling table (Worker → Chunk assignment)
# - Processing time (Total + Per chunk)
# - Fault tolerance status
# - Gate lock (no data without master)
# ============================================

import streamlit as st
import json
import plotly.graph_objects as go
import os
import pandas as pd
import psutil
from datetime import datetime

# Page config
st.set_page_config(
    page_title="DCDAS | Crime Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🛡️"
)

# ── DATA LOADER ──
DATA_FILE = 'outputs/dashboard_data.json'

def load_dashboard_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    return None

def load_transformed_data_sample(n_rows=20000):
    """Load sample of transformed data for advanced analytics"""
    try:
        path = 'datasets/processed/CRIME_DATA_TRANSFORMED.csv'
        if os.path.exists(path):
            return pd.read_csv(path, nrows=n_rows)
    except Exception:
        pass
    return None

live_data = load_dashboard_data()
full_data_sample = load_transformed_data_sample()

# ── CSS STYLING ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Outfit:wght@300;400;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg-base:      #06080d;
    --bg-surface:   #0c0f18;
    --bg-card:      #111520;
    --bg-elevated:  #181d2e;
    --accent-blue:  #5294ff;
    --accent-cyan:  #00d4ff;
    --accent-green: #00ffb3;
    --accent-amber: #ffbe5e;
    --accent-red:   #ff6b6b;
    --accent-purple:#b69eff;
    --text-primary: #ffffff;
    --text-secondary:#e2e8f0;
    --text-muted:   #cbd5e1;
    --border:       #242f4d;
    --border-bright:#3b4d7c;
}

.stApp { background-color: var(--bg-base) !important; font-family: 'Outfit', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem !important; max-width: 100% !important; }

/* Hero Section */
.premium-hero {
    background: linear-gradient(180deg, rgba(12, 15, 24, 0.95) 0%, rgba(6, 8, 13, 0.98) 100%);
    border: 2px solid var(--border-bright);
    border-top: 5px solid var(--accent-blue);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
    text-align: center;
}
.hero-meta-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.3em;
    color: var(--accent-cyan);
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.hero-main-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.25;
}
.hero-main-title span {
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub-desc {
    font-size: 1rem;
    color: var(--text-muted);
    margin-top: 1rem;
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
}
.system-badge-container {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 1.5rem;
    flex-wrap: wrap;
}
.sys-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 1.2rem;
    border-radius: 30px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
}
.sb-live  { background: rgba(0, 255, 179, 0.12); border: 1px solid rgba(0, 255, 179, 0.4); color: var(--accent-green); }
.sb-node  { background: rgba(82, 148, 255, 0.12); border: 1px solid rgba(82, 148, 255, 0.4); color: var(--text-primary); }
.sb-shard { background: rgba(255, 190, 94, 0.12); border: 1px solid rgba(255, 190, 94, 0.4); color: var(--accent-amber); }

/* Cards */
.premium-card-v2 {
    background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-surface) 100%);
    border: 2px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem;
    transition: all 0.3s;
}
.premium-card-v2:hover {
    border-color: var(--border-bright);
    transform: translateY(-2px);
}
.glow-b { border-left: 4px solid var(--accent-blue); }
.glow-c { border-left: 4px solid var(--accent-cyan); }
.glow-p { border-left: 4px solid var(--accent-purple); }
.glow-g { border-left: 4px solid var(--accent-green); }

.card-label-v2 {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--accent-cyan);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.6rem;
}
.card-value-v2 {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1;
}
.card-subtext-v2 {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-top: 0.5rem;
}

/* Section Title */
.section-title-v2 {
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--text-primary);
    margin-top: 2rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Standby Wrapper */
.standby-wrapper {
    background: #0c0f18;
    border: 2px dashed #242f4d;
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    margin-top: 1rem;
}
.standby-title {
    font-size: 1.3rem;
    color: var(--accent-amber);
    font-weight: 700;
    margin-bottom: 0.5rem;
}
.standby-desc {
    font-size: 0.9rem;
    color: var(--text-muted);
}

/* Node Cards */
.node-card-v2 {
    background: #0f1322;
    border: 2px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem;
}
.node-header-v2 {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
    margin-bottom: 0.8rem;
}
.node-name-v2 {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text-primary);
}
.node-tag-v2 {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
}
.tag-online { background: rgba(0, 255, 179, 0.15); color: var(--accent-green); }
.tag-offline { background: rgba(255, 107, 107, 0.15); color: var(--accent-red); }
.node-row-v2 {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-bottom: 0.3rem;
}
.node-val-v2 {
    color: var(--text-primary);
    font-weight: 600;
}

/* Progress Row */
.prog-row {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 0.55rem;
}
.prog-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-secondary);
    width: 80px;
    flex-shrink: 0;
}
.prog-bg {
    flex: 1;
    background: var(--bg-elevated);
    border-radius: 4px;
    height: 6px;
    overflow: hidden;
}
.prog-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
}
.pf-green {
    background: linear-gradient(90deg, var(--accent-green), #4fffca);
}
.prog-pct {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-secondary);
    width: 80px;
    text-align: right;
}

/* Data Table */
.dataframe-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    padding: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── HERO HEADER ──
st.markdown("""
<div class="premium-hero">
    <div class="hero-meta-tag">⚡ DCDAS SYSTEM</div>
    <div class="hero-main-title">Distributed Crime Data<br><span>Analysis System</span></div>
    <div class="hero-sub-desc">
        Master-Worker cluster with TCP socket streaming, zlib compression, and real-time analytics.
    </div>
    <div class="system-badge-container">
        <span class="sys-badge sb-live">● SYSTEM READY</span>
        <span class="sys-badge sb-node">🛡️ MASTER NODE</span>
        <span class="sys-badge sb-shard">📦 10 PARTITIONS</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TABS: ANALYTICS FIRST, HARDWARE SECOND ──
tab_analytics, tab_hardware = st.tabs(["📊 CRIME ANALYTICS", "⚙️ SYSTEM HEALTH & HARDWARE PERFORMANCE"])

# Check pipeline state
is_processing = False
is_completed = False
has_master_started = False

if live_data:
    state = live_data.get("pipeline_state", "standby")
    if state == "processing":
        is_processing = True
        has_master_started = True
    elif state == "completed":
        is_completed = True
        has_master_started = True

# ============================================================
# TAB 1: CRIME ANALYTICS
# ============================================================
with tab_analytics:
    if not has_master_started:
        st.markdown("""
        <div class="standby-wrapper" style="border-color: var(--accent-red);">
            <div class="standby-title" style="color: var(--accent-red);">🔒 Processing Pipeline Not Started</div>
            <div class="standby-desc" style="font-size:1rem;">
                Start master.py to begin data processing.
            </div>
            <div style="color: var(--text-muted); font-size: 0.8rem; margin-top: 0.8rem;">
                Command: python distributed/master.py
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        chunks_done = live_data.get("chunks_completed", 0)

        # ── NEW: chunks_done == 0 guard ──
        if chunks_done == 0:
            st.markdown("""
            <div class="standby-wrapper" style="border-color: var(--accent-amber);">
                <div class="standby-title">⏳ Loading Data...</div>
                <div class="standby-desc">Master is running. Waiting for first chunk to complete before showing analytics.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            total_crimes = live_data.get("total_crimes", 0)
            crime_types = live_data.get("crime_types", {})
            monthly = live_data.get("monthly_trends", {})
            outcomes = live_data.get("outcomes", {})
            
            # KPI Cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="premium-card-v2 glow-b">
                    <div class="card-label-v2">📊 TOTAL CRIMES Record / UK Cities Dataset</div>
                    <div class="card-value-v2">{total_crimes:,}</div>
                    <div class="card-subtext-v2">{chunks_done}/10 chunks done</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                top_crime = max(crime_types.items(), key=lambda x: x[1])[0] if crime_types else "Loading..."
                st.markdown(f"""
                <div class="premium-card-v2 glow-c">
                    <div class="card-label-v2">🔥 TOP CRIME TYPE</div>
                    <div class="card-value-v2" style="font-size:1.3rem;">{top_crime[:30]}</div>
                    <div class="card-subtext-v2">Most frequent offence</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="premium-card-v2 glow-g">
                    <div class="card-label-v2">📅 DATA TIMEFRAME</div>
                    <div class="card-value-v2">2023-2026</div>
                    <div class="card-subtext-v2">36 months coverage</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                unique_types = len(crime_types)
                st.markdown(f"""
                <div class="premium-card-v2 glow-p">
                    <div class="card-label-v2">📈 CRIME TYPES</div>
                    <div class="card-value-v2">{unique_types}</div>
                    <div class="card-subtext-v2">Distinct categories</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Chart 1: Crime Type Distribution
            st.markdown('<div class="section-title-v2">📊 Crime Type Distribution</div>', unsafe_allow_html=True)
            if crime_types:
                df_crime = pd.DataFrame(list(crime_types.items()), columns=['Type', 'Count']).sort_values('Count', ascending=False).head(10)
                fig1 = go.Figure(data=[go.Pie(labels=df_crime['Type'], values=df_crime['Count'], hole=0.45, textinfo='percent+label', textposition='auto', marker=dict(colors=['#5294ff', '#ffbe5e', '#ff6b6b', '#b69eff', '#00ffb3', '#00d4ff', '#ff8cc6', '#8edba3', '#a2a2a2', '#7fb0c9']))])
                fig1.update_layout(title="Top 10 Crime Types by Volume", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=450, font=dict(color='#cbd5e1'))
                st.plotly_chart(fig1, use_container_width=True)
            
            # Chart 2: Monthly Trend
            st.markdown('<div class="section-title-v2">📅 Monthly Crime Trends</div>', unsafe_allow_html=True)
            if monthly:
                df_monthly = pd.DataFrame(list(monthly.items()), columns=['Month', 'Count'])
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=df_monthly['Month'], y=df_monthly['Count'], mode='lines+markers', line=dict(color='#5294ff', width=3), marker=dict(size=8, color='#00d4ff'), fill='tozeroy', fillcolor='rgba(82,148,255,0.1)'))
                fig2.update_layout(title="Crime Incidents Over Time", xaxis_title="Month", yaxis_title="Number of Incidents", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, font=dict(color='#cbd5e1'), xaxis=dict(gridcolor='#242f4d'), yaxis=dict(gridcolor='#242f4d'))
                st.plotly_chart(fig2, use_container_width=True)
            
                      
                            # Chart 3: Crime Hotspot Map (Google Maps Style)
            st.markdown('<div class="section-title-v2">📍 Crime Hotspot Map (Interactive)</div>', unsafe_allow_html=True)
            
            if full_data_sample is not None and 'Latitude' in full_data_sample.columns and 'Longitude' in full_data_sample.columns:
                # Take sample of data for performance
                heatmap_df = full_data_sample[['Latitude', 'Longitude', 'Crime type', 'Location', 'LSOA name', 'Reported by']].dropna().head(8000)
                
                if len(heatmap_df) > 0:
                    # Extract meaningful location names
                    def extract_place_name(row):
                        location = str(row.get('Location', ''))
                        lsoa = str(row.get('LSOA name', ''))
                        police = str(row.get('Reported by', ''))
                        
                        # Clean location
                        location = location.replace("On or near ", "").replace("On or near", "").strip()
                        
                        # Common UK cities/areas to check
                        cities = ['London', 'Manchester', 'Birmingham', 'Leeds', 'Liverpool', 
                                 'Newcastle', 'Bristol', 'Sheffield', 'Cambridge', 'Oxford',
                                 'Nottingham', 'Leicester', 'Coventry', 'Bradford', 'Cardiff',
                                 'Southampton', 'Portsmouth', 'Derby', 'Wolverhampton']
                        
                        # Try to find city name in location or LSOA
                        for city in cities:
                            if city.lower() in location.lower() or city.lower() in lsoa.lower():
                                return city
                        
                        # Try to get from police force
                        police_name = police.replace(" Constabulary", "").strip()
                        if len(police_name) > 0 and len(police_name) < 25:
                            return police_name
                        
                        # Return first part of location or LSOA
                        if len(location) > 5 and location != 'nan':
                            return location[:25]
                        elif len(lsoa) > 5 and lsoa != 'nan':
                            return lsoa[:25]
                        else:
                            return f"Area ({round(row['Latitude'], 1)}, {round(row['Longitude'], 1)})"
                    
                    heatmap_df['PlaceName'] = heatmap_df.apply(extract_place_name, axis=1)
                    
                    # Create hover text
                    def create_hover_text(row):
                        place = row['PlaceName']
                        crime = str(row.get('Crime type', 'Unknown'))[:35]
                        location = str(row.get('Location', ''))[:40].replace("On or near ", "")
                        
                        hover_text = f"<b>📍 {place}</b><br>"
                        hover_text += f"📊 {crime}<br>"
                        hover_text += f"📍 {location}"
                        
                        return hover_text
                    
                    heatmap_df['HoverText'] = heatmap_df.apply(create_hover_text, axis=1)
                    
                    # Create figure with OpenStreetMap style (Google Maps like)
                    fig3 = go.Figure()
                    
                    # Density heatmap layer
                    fig3.add_trace(go.Densitymapbox(
                        lat=heatmap_df['Latitude'],
                        lon=heatmap_df['Longitude'],
                        radius=10,
                        colorscale=[
                            [0, 'rgba(255,0,0,0)'],
                            [0.3, 'rgba(255,100,0,0.3)'],
                            [0.6, 'rgba(255,50,0,0.6)'],
                            [1, 'rgba(255,0,0,0.9)']
                        ],
                        showscale=True,
                        colorbar=dict(
                            title="Crime<br>Density",
                            tickfont=dict(color='#cbd5e1', size=9),
                            thickness=12,
                            x=0.95
                        ),
                        opacity=0.7,
                        name='Crime Density'
                    ))
                    
                    # Add markers
                    fig3.add_trace(go.Scattermapbox(
                        lat=heatmap_df['Latitude'],
                        lon=heatmap_df['Longitude'],
                        mode='markers',
                        marker=dict(size=4, color='#ff4444', opacity=0.3),
                        text=heatmap_df['HoverText'],
                        hoverinfo='text',
                        hoverlabel=dict(
                            bgcolor='rgba(0,0,0,0.8)',
                            font=dict(color='#ffffff', size=11),
                            bordercolor='#ff4444'
                        ),
                        name='Crime Locations',
                        visible='legendonly'
                    ))
                    
                    # Center on UK
                    center_lat = 52.5
                    center_lon = -1.5
                    
                    fig3.update_layout(
                        mapbox=dict(
                            style='open-street-map',  # Google Maps style!
                            center=dict(lat=center_lat, lon=center_lon),
                            zoom=5.5,
                        ),
                        margin=dict(l=0, r=0, t=25, b=0),
                        height=450,
                        paper_bgcolor='rgba(0,0,0,0)',
                        legend=dict(
                            font=dict(color='#cbd5e1', size=9),
                            bgcolor='rgba(0,0,0,0)',
                            x=0.01,
                            y=0.99
                        )
                    )
                    
                    st.plotly_chart(fig3, use_container_width=True)
                    
                    # Map instructions
                    st.markdown("""
                    <div style="background:#0c0f18; border-radius:8px; padding:8px 12px; margin-top:5px;">
                        <span style="color:#00d4ff;">🔍</span> <span style="color:#cbd5e1; font-size:12px;">Hover anywhere to see location details | </span>
                        <span style="color:#ff6b6b;">🔴</span> <span style="color:#cbd5e1; font-size:12px;">Red areas = high crime density | </span>
                        <span style="color:#00ffb3;">👁️</span> <span style="color:#cbd5e1; font-size:12px;">Toggle markers from legend</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    st.info("📊 Loading crime location data...")
            else:
                st.info("📍 Crime hotspot map will appear after data processing")

            # Chart 4: High-Risk Areas
            st.markdown('<div class="section-title-v2">⚠️ High-Risk Areas</div>', unsafe_allow_html=True)
            if full_data_sample is not None and 'Location' in full_data_sample.columns:
                location_counts = full_data_sample['Location'].str.replace('On or near ', '').value_counts().head(10)
                fig4 = go.Figure(go.Bar(x=location_counts.values, y=location_counts.index, orientation='h', marker=dict(color=location_counts.values, colorscale='Reds', showscale=False), text=location_counts.values, textposition='outside'))
                fig4.update_layout(title="Top 10 High-Risk Locations", xaxis_title="Number of Incidents", yaxis_title="Location", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, font=dict(color='#cbd5e1'), xaxis=dict(gridcolor='#242f4d'))
                st.plotly_chart(fig4, use_container_width=True)
            
            # Chart 5: Police Force
            st.markdown('<div class="section-title-v2">👮 Police Force Comparison</div>', unsafe_allow_html=True)
            if full_data_sample is not None and 'Reported by' in full_data_sample.columns:
                police_counts = full_data_sample['Reported by'].value_counts().head(8)
                fig5 = go.Figure(go.Bar(x=police_counts.index, y=police_counts.values, marker=dict(color='#5294ff'), text=police_counts.values, textposition='outside'))
                fig5.update_layout(title="Crime Reports by Police Force", xaxis_title="Police Force", yaxis_title="Number of Reports", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, font=dict(color='#cbd5e1'), xaxis=dict(tickangle=45, gridcolor='#242f4d'), yaxis=dict(gridcolor='#242f4d'))
                st.plotly_chart(fig5, use_container_width=True)
            
            # Chart 6: Case Outcomes
            st.markdown('<div class="section-title-v2">⚖️ Case Outcomes</div>', unsafe_allow_html=True)
            if outcomes:
                df_outcomes = pd.DataFrame(list(outcomes.items()), columns=['Outcome', 'Count']).sort_values('Count', ascending=False).head(8)
                fig6 = go.Figure(go.Bar(x=df_outcomes['Count'], y=df_outcomes['Outcome'], orientation='h', marker=dict(color=df_outcomes['Count'], colorscale='Tealgrn', showscale=False), text=df_outcomes['Count'], textposition='outside'))
                fig6.update_layout(title="Most Common Case Outcomes", xaxis_title="Number of Cases", yaxis_title="Outcome", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=450, font=dict(color='#cbd5e1'), xaxis=dict(gridcolor='#242f4d'))
                st.plotly_chart(fig6, use_container_width=True)


# ============================================================
# TAB 2: SYSTEM HEALTH & PERFORMANCE (FIXED - NO DUPLICATION)
# ============================================================
with tab_hardware:
    st.markdown('<div class="section-title-v2">⚡ System Performance</div>', unsafe_allow_html=True)
    
    if not has_master_started:
        st.markdown("""
        <div class="standby-wrapper">
            <div class="standby-title">⏳ Waiting for Master Node</div>
            <div class="standby-desc">Start master.py to see system metrics</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        chunks_done = live_data.get("chunks_completed", 0)

        if chunks_done == 0:
            st.markdown("""
            <div class="standby-wrapper" style="border-color: var(--accent-amber);">
                <div class="standby-title">⏳ Loading System Data...</div>
                <div class="standby-desc">Master is running. Waiting for first chunk to complete before showing system metrics.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            m_cpu = live_data.get("master_system", {}).get("cpu", 0)
            m_ram = live_data.get("master_system", {}).get("ram", 0)
            m_status = live_data.get("live_status", {}).get("Master-Node", {}).get("status", "Active")
            scheduling_info = live_data.get("scheduling_info", [])
            fault_count = live_data.get("fault_events_count", 0)
            
            # FILTER: Sirf real workers lo, "Master-Local" ko filter karo
            all_workers = live_data.get("worker_stats", {})
            workers_dict = {}
            for w_id, w_info in all_workers.items():
                # Skip Master-Local, Master-Backup, etc. - sirf real workers
                if "Master" not in w_id:
                    workers_dict[w_id] = w_info
            
            # Calculate total processing time
            total_time = 0
            chunk_times = {}
            master_chunks_count = 0
            for log in scheduling_info:
                if "time" in log:
                    total_time += log["time"]
                    chunk_times[log["chunk"]] = log["time"]
                    # Count master chunks from scheduling info
                    if log.get("worker") == "Master" or "Master" in str(log.get("worker", "")):
                        master_chunks_count += 1
            
            # MASTER CARD with Time
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f"""
                <div class="node-card-v2" style="border-left: 4px solid var(--accent-blue);">
                    <div class="node-header-v2">
                        <span class="node-name-v2">🖥️ MASTER SYSTEM</span>
                        <span class="node-tag-v2 tag-online">ACTIVE</span>
                    </div>
                    <div class="node-row-v2"><span>Status:</span><span class="node-val-v2">{m_status}</span></div>
                    <div class="node-row-v2"><span>CPU:</span><span class="node-val-v2">{m_cpu}%</span></div>
                    <div class="node-row-v2"><span>RAM:</span><span class="node-val-v2">{m_ram}%</span></div>
                    <div class="node-row-v2"><span>Chunks:</span><span class="node-val-v2">{master_chunks_count}/10</span></div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_time = round(total_time / max(chunks_done, 1), 2)
                st.markdown(f"""
                <div class="premium-card-v2 glow-c">
                    <div class="card-label-v2">⏱️ PROCESSING TIME</div>
                    <div class="card-value-v2" style="font-size:1.5rem;">Total: {total_time}s</div>
                    <div class="card-subtext-v2">Avg per chunk: {avg_time}s | Faults: {fault_count}</div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(int((chunks_done / 10) * 100) / 100)
            
            # ===== WORKER NODES CARDS (Sirf Real Workers) =====
            st.markdown('<div class="section-title-v2">💻 Worker Nodes Performance</div>', unsafe_allow_html=True)
            
            if workers_dict:
                worker_items = list(workers_dict.items())
                num_workers = len(worker_items)
                cols = st.columns(min(num_workers, 3))
                
                for idx, (w_id, w_info) in enumerate(worker_items):
                    ip = w_id.replace("Worker-", "")
                    w_cpu = w_info.get("cpu", 0)
                    w_ram = w_info.get("ram", 0)
                    w_last_chunk = w_info.get("last_processed_chunk", "-")
                    w_time = w_info.get("processing_time", 0)
                    w_status = w_info.get("status", "IDLE")
                    
                    status_color = "tag-online" if "DONE" in w_status or "CONNECTED" in w_status else "tag-offline"
                    status_text = "ACTIVE" if "DONE" in w_status or "CONNECTED" in w_status else w_status
                    
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div class="node-card-v2" style="border-left: 4px solid var(--accent-green);">
                            <div class="node-header-v2">
                                <span class="node-name-v2">💻 WORKER ({ip})</span>
                                <span class="node-tag-v2 {status_color}">{status_text}</span>
                            </div>
                            <div class="node-row-v2"><span>CPU:</span><span class="node-val-v2">{w_cpu}%</span></div>
                            <div class="node-row-v2"><span>RAM:</span><span class="node-val-v2">{w_ram}%</span></div>
                            <div class="node-row-v2"><span>Last Chunk:</span><span class="node-val-v2">{w_last_chunk}</span></div>
                            <div class="node-row-v2"><span>Time:</span><span class="node-val-v2">{w_time}s</span></div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Worker Details Table
                st.markdown('<div class="section-title-v2" style="margin-top:1rem;">📋 Worker Details Table</div>', unsafe_allow_html=True)
                worker_data = []
                for w_id, w_info in workers_dict.items():
                    ip = w_id.replace("Worker-", "")
                    worker_data.append({
                        "Worker IP": ip,
                        "Last Chunk": w_info.get("last_processed_chunk", "-"),
                        "CPU %": w_info.get("cpu", 0),
                        "RAM %": w_info.get("ram", 0),
                        "Time (s)": w_info.get("processing_time", 0),
                        "Status": w_info.get("status", "IDLE")
                    })
                df_workers = pd.DataFrame(worker_data)
                st.dataframe(df_workers, use_container_width=True, height=200)
            else:
                st.markdown("""
                <div class="standby-wrapper">
                    <div class="standby-title">⏳ No Workers Connected</div>
                    <div class="standby-desc">Connect worker nodes to see performance metrics</div>
                </div>
                """, unsafe_allow_html=True)
            
            # SCHEDULING TABLE
            st.markdown('<div class="section-title-v2">📋 Task Scheduling (Chunk Assignment)</div>', unsafe_allow_html=True)
            
            if scheduling_info:
                schedule_data = []
                for log in scheduling_info:
                    worker_name = log.get("worker", "Unknown")
                    # Clean worker name
                    if "Master" in worker_name:
                        worker_name = "Master"
                    else:
                        worker_name = worker_name.replace("Worker-", "")
                    schedule_data.append({
                        "Chunk": f"Chunk {log.get('chunk', '-')}",
                        "Assigned To": worker_name,
                        "Time Taken": f"{log.get('time', 0)}s"
                    })
                df_schedule = pd.DataFrame(schedule_data)
                st.dataframe(df_schedule, use_container_width=True, height=250)
            else:
                st.markdown("""
                <div class="standby-wrapper">
                    <div class="standby-title">📋 No Tasks Scheduled Yet</div>
                    <div class="standby-desc">Schedule will appear when chunks are assigned to workers</div>
                </div>
                """, unsafe_allow_html=True)
            
            # SUMMARY STATS
            st.markdown('<div class="section-title-v2">📊 Processing Summary</div>', unsafe_allow_html=True)
            
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.markdown(f"""
                <div class="premium-card-v2 glow-g">
                    <div class="card-label-v2">📦 TOTAL CHUNKS</div>
                    <div class="card-value-v2">10</div>
                    <div class="card-subtext-v2">{chunks_done} processed</div>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div class="premium-card-v2 glow-b">
                    <div class="card-label-v2">⏱️ TOTAL TIME</div>
                    <div class="card-value-v2">{total_time}s</div>
                    <div class="card-subtext-v2">Full processing</div>
                </div>
                """, unsafe_allow_html=True)
            with col_c:
                st.markdown(f"""
                <div class="premium-card-v2 glow-c">
                    <div class="card-label-v2">⚡ AVG PER CHUNK</div>
                    <div class="card-value-v2">{avg_time}s</div>
                    <div class="card-subtext-v2">Per chunk average</div>
                </div>
                """, unsafe_allow_html=True)
            with col_d:
                st.markdown(f"""
                <div class="premium-card-v2 glow-p">
                    <div class="card-label-v2">🔁 FAULT EVENTS</div>
                    <div class="card-value-v2">{fault_count}</div>
                    <div class="card-subtext-v2">Auto recovered</div>
                </div>
                """, unsafe_allow_html=True)
            
            # CHUNK PROGRESS
            st.markdown('<div class="section-title-v2">📦 Chunk Progress Details</div>', unsafe_allow_html=True)
            
            chunk_rows_html = ""
            chunk_time_map = {}
            for log in scheduling_info:
                chunk_num = str(log.get("chunk", ""))
                chunk_time_map[chunk_num] = log.get("time", 0)
            
            for i in range(1, 11):
                done = i <= chunks_done
                status_text = "✅ Done" if done else "⏳ Waiting"
                width = "100" if done else "0"
                fill_class = "pf-green" if done else ""
                time_val = chunk_time_map.get(str(i), chunk_time_map.get(i, 0))
                time_str = f"{time_val}s" if time_val and time_val > 0 else "—"
                
                chunk_rows_html += '<div class="prog-row"><div class="prog-lbl">Chunk-{0:02d}</div><div class="prog-bg"><div class="prog-fill {1}" style="width:{2}%"></div></div><div class="prog-pct" style="min-width:70px;">{3}</div><div class="prog-pct" style="width:60px; color:var(--accent-cyan);">{4}</div></div>'.format(i, fill_class, width, status_text, time_str)
            
            st.markdown("""
            <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:1.2rem;">
                <div class="card-label-v2" style="margin-bottom:0.8rem;">CHUNK STATUS &amp; PROCESSING TIME</div>
                """ + chunk_rows_html + """
            </div>
            """, unsafe_allow_html=True)
            
            # FAULT PROTECTION STATUS
            st.markdown('<div class="section-title-v2">🛡️ Fault Tolerance</div>', unsafe_allow_html=True)
            
            col_x, col_y, col_z = st.columns(3)
            with col_x:
                # Sirf real workers count (Master-Local exclude)
                total_active_nodes = len(workers_dict) + 1  # +1 for Master
                st.markdown(f"""
                <div class="premium-card-v2 glow-g">
                    <div class="card-label-v2">✅ ACTIVE NODES</div>
                    <div class="card-value-v2">{total_active_nodes}</div>
                    <div class="card-subtext-v2">Master + {len(workers_dict)} Workers</div>
                </div>
                """, unsafe_allow_html=True)
            with col_y:
                st.markdown(f"""
                <div class="premium-card-v2">
                    <div class="card-label-v2">⚠️ FAILURES</div>
                    <div class="card-value-v2">{fault_count}</div>
                    <div class="card-subtext-v2">Auto recovered</div>
                </div>
                """, unsafe_allow_html=True)
            with col_z:
                fallback_status = "Active" if chunks_done > 0 and len(workers_dict) == 0 else "Standby"
                st.markdown(f"""
                <div class="premium-card-v2 glow-c">
                    <div class="card-label-v2">🔁 BACKUP MODE</div>
                    <div class="card-value-v2">{fallback_status}</div>
                    <div class="card-subtext-v2">Master self processing</div>
                </div>
                """, unsafe_allow_html=True)
            
            # MASTER & WORKERS PROGRESS
            st.markdown('<div class="section-title-v2">📊 Master & Workers Progress (Chunks Processed)</div>', unsafe_allow_html=True)
            
            # Count chunks per worker from scheduling_info
            worker_chunk_count = {}
            worker_last_time = {}
            
            for log in scheduling_info:
                worker = log.get("worker", "Unknown")
                time_taken = log.get("time", 0)
                
                # Clean worker name for display
                if "Master" in worker:
                    display_worker = "Master"
                else:
                    display_worker = worker.replace("Worker-", "")
                
                if display_worker not in worker_chunk_count:
                    worker_chunk_count[display_worker] = 0
                    worker_last_time[display_worker] = 0
                
                worker_chunk_count[display_worker] += 1
                if time_taken > worker_last_time[display_worker]:
                    worker_last_time[display_worker] = time_taken
            
            # Master progress
            master_count = worker_chunk_count.get("Master", 0)
            master_percent = int((master_count / 10) * 100)
            
            st.markdown(f"""
            <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:1rem;margin-bottom:0.8rem;">
                <div class="prog-row">
                    <div class="prog-lbl" style="width:140px;">🖥️ MASTER (192.168.100.15)</div>
                    <div class="prog-bg"><div class="prog-fill {'pf-green' if master_count > 0 else ''}" style="width:{master_percent}%"></div></div>
                    <div class="prog-pct" style="min-width:100px;">{master_count} / 10 chunks</div>
                    <div class="prog-pct" style="width:60px; color:var(--accent-cyan);">{worker_last_time.get('Master', 0)}s</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Workers progress (only real workers, no Master-Local)
            for ip in workers_dict.keys():
                worker_ip = ip.replace("Worker-", "")
                worker_count = worker_chunk_count.get(worker_ip, 0)
                worker_percent = int((worker_count / 10) * 100)
                last_time = worker_last_time.get(worker_ip, 0)
                
                st.markdown(f"""
                <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:1rem;margin-bottom:0.8rem;">
                    <div class="prog-row">
                        <div class="prog-lbl" style="width:140px;">💻 WORKER ({worker_ip})</div>
                        <div class="prog-bg"><div class="prog-fill {'pf-green' if worker_count > 0 else ''}" style="width:{worker_percent}%"></div></div>
                        <div class="prog-pct" style="min-width:100px;">{worker_count} / 10 chunks</div>
                        <div class="prog-pct" style="width:60px; color:var(--accent-cyan);">{last_time}s</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Total Progress
            total_percent = int((chunks_done / 10) * 100)
            st.markdown(f"""
            <div style="background:linear-gradient(135deg, #0f1420, #0a0e17);border:1px solid var(--accent-blue);border-radius:10px;padding:1rem;margin-top:0.5rem;">
                <div class="prog-row">
                    <div class="prog-lbl" style="width:140px; color:var(--accent-green);">📦 TOTAL PROGRESS</div>
                    <div class="prog-bg"><div class="prog-fill pf-green" style="width:{total_percent}%"></div></div>
                    <div class="prog-pct" style="min-width:100px; color:var(--accent-green);">{chunks_done} / 10 chunks</div>
                    <div class="prog-pct" style="width:60px;">{total_percent}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)