import streamlit as st
import json
import os
import time
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from monitor import WebsiteMonitor 

CONFIG_FILE = "config.json"
LOG_FILE = "uptime_log.csv"

# -------------------------
# Page Setup & Professional Styling
# -------------------------
st.set_page_config(page_title="UptimePulse Pro", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    /* Global Background */
    .block-container {padding-top: 1.5rem; background-color: #f8fafc;}
    
    /* --- SIDEBAR HIGH-CONTRAST FIX --- */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }

    [data-testid="stSidebar"] .stWidgetLabel p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stMarkdown p {
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }

    /* Sidebar Section Headers */
    [data-testid="stSidebar"] h3 {
        color: #38bdf8 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 1.5rem !important;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 5px;
    }

    /* Input Field Visibility Fix */
    [data-testid="stSidebar"] .stTextInput input, 
    [data-testid="stSidebar"] .stNumberInput input {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
    }

    /* PLACEHOLDER VISIBILITY FIX */
    [data-testid="stSidebar"] input::placeholder {
        color: #94a3b8 !important;
        opacity: 1; 
    }

    /* SLIDER TICK/SCALE VISIBILITY FIX */
    [data-testid="stSidebar"] [data-testid="stTickBarMin"],
    [data-testid="stSidebar"] [data-testid="stTickBarMax"],
    [data-testid="stSidebar"] [data-baseweb="slider"] div {
        color: #cbd5e1 !important;
        opacity: 1 !important;
        font-size: 0.75rem !important;
    }

    /* Sidebar Buttons */
    [data-testid="stSidebar"] button[kind="primary"] {
        background-color: #ef4444 !important; 
        color: white !important;
        width: 100%;
    }
    [data-testid="stSidebar"] button[kind="secondary"] {
        background-color: transparent !important;
        color: #94a3b8 !important;
        border: 1px solid #334155 !important;
        width: 100%;
    }

    /* --- DASHBOARD COMPONENTS --- */
    h2 {color: #1e293b; font-weight: 800 !important;}
    
    .kpi-card {
        background: white; padding: 1.2rem; border-radius: 12px; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0;
    }

    .stButton button {
        margin-top: 20px !important;
        margin-bottom: 10px !important;
    }

    /* Ensures the header doesn't collide with the cards */
    header[data-testid="stHeader"] {
        z-index: 100;
    }

    .metric-container {
        display: flex;
        justify-content: space-between;
        padding: 0 5px;
        margin-top: 10px;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
    }
    .metric-val {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
    }

    /* Pulse Animation */
    .status-pulse {
        height: 10px; width: 10px; background-color: #10b981;
        border-radius: 50%; display: inline-block; margin-right: 8px;
        box-shadow: 0 0 8px #10b981;
        animation: pulse-animation 2s infinite;
    }
    @keyframes pulse-animation {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------
# Core Logic
# -------------------------
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f: return json.load(f)
    return []

def save_config(sites):
    with open(CONFIG_FILE, "w") as f: json.dump(sites, f, indent=4)

def log_result(url, status, response_time):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_data = pd.DataFrame([[now, url, status, response_time]], 
                            columns=["Timestamp", "URL", "Status", "Latency"])
    log_data.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False)

# -------------------------
# Sidebar
# -------------------------
with st.sidebar:
    st.markdown("<h2 style='color: white; font-size: 1.6rem;'>⚡ UptimePulse</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 0.8rem; margin-top: -15px;'>v2.1 Network Intelligence</p>", unsafe_allow_html=True)
    
    st.markdown("### 🛰️ Monitoring Target")
    new_url = st.text_input("URL Address", placeholder="https://example.com")
    max_time = st.number_input("Latency Limit (s)", 0.1, 10.0, 2.0)

    # Shift the button down slightly
    st.markdown('<div style="margin-top: 8px;"></div>', unsafe_allow_html=True)

    if st.button("➕ Add Target", type="primary", use_container_width=True):
        if new_url.startswith("http"):
            sites = load_config()
            sites.append({"url": new_url, "max_response_time": max_time})
            save_config(sites)
            st.rerun()
    
    st.markdown("### ⚙️ Engine Controls")
    refresh_interval = st.select_slider("Scan Frequency (s)", options=[5, 10, 30, 60], value=10)
    
    st.markdown("### 🧹 Maintenance")
    if st.button("Flush Monitoring Data", type="secondary"):
        save_config([])
        if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
        st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.session_state.get('monitoring', False):
        st.markdown(f"<div style='text-align: center;'><span class='status-pulse'></span> <span style='color: #10b981; font-weight: bold;'>Engine Active</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align: center; color: #64748b;'>Engine Standby</div>", unsafe_allow_html=True)

# -------------------------
# Header
# -------------------------
h_col1, h_col2 = st.columns([5, 1])
with h_col1:
    st.markdown("## 🌐 Network Control Center")
with h_col2:
    if "monitoring" not in st.session_state: st.session_state.monitoring = False
    btn_label = "⏹ STOP" if st.session_state.monitoring else "▶ START"
    if st.button(btn_label, use_container_width=True, type="primary" if not st.session_state.monitoring else "secondary"):
        st.session_state.monitoring = not st.session_state.monitoring
        st.rerun()

# -------------------------
# Main Execution
# -------------------------
sites = load_config()

if not sites:
    st.info("System Ready. Please define a monitoring target in the sidebar.")
elif st.session_state.monitoring:
    monitor = WebsiteMonitor(sites)
    results = monitor.run_check()
    
    total_sites = len(results)
    online_sites = sum(1 for r in results if r["status"] == "UP")
    offline_sites = total_sites - online_sites

    # KPI Row
    st.markdown(f"""
        <div style="display: flex; gap: 20px; margin-bottom: 25px; margin-top: 10px;">
            <div class="kpi-card" style="flex:1; border-left: 5px solid #6366f1;">
                <p style="color: #64748b; margin: 0; font-size: 0.75rem; font-weight: 700;">TOTAL ENDPOINTS</p>
                <p style="margin: 0; font-size: 1.8rem; font-weight: 800; color: #1e293b;">{total_sites}</p>
            </div>
            <div class="kpi-card" style="flex:1; border-left: 5px solid #10b981;">
                <p style="color: #64748b; margin: 0; font-size: 0.75rem; font-weight: 700;">SYSTEMS ONLINE</p>
                <p style="margin: 0; font-size: 1.8rem; font-weight: 800; color: #10b981;">{online_sites}</p>
            </div>
            <div class="kpi-card" style="flex:1; border-left: 5px solid #ef4444;">
                <p style="color: #64748b; margin: 0; font-size: 0.75rem; font-weight: 700;">CRITICAL FAILURES</p>
                <p style="margin: 0; font-size: 1.8rem; font-weight: 800; color: #ef4444;">{offline_sites}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    grid_cols = st.columns(3)
    for idx, r in enumerate(results):
        log_result(r['url'], r['status'], r['response_time'])
        
        if r["status"] != "UP":
            st.toast(f"CRITICAL: {r['url']} unreachable", icon="🚨")

        with grid_cols[idx % 3]:
            status_color = "#10b981" if r["status"] == "UP" else "#ef4444"
            status_bg = "#f0fdf4" if r["status"] == "UP" else "#fef2f2"
            res_time = r['response_time'] if r['response_time'] else 0
            
            st.markdown(f"""
                <div style="background-color: {status_bg}; border: 1px solid {status_color}; padding: 15px; border-radius: 10px; margin-top: 10px;">
                    <span style="color: {status_color}; font-size: 0.7rem; font-weight: 800; text-transform: uppercase;">{r['status']}</span>
                    <h3 style="margin-bottom: 10px; color: #1e293b;">{r['url'].replace('https://','').replace('http://','')}</h3>
                    <div class="metric-container">
                        <div>
                            <div class="metric-label">Latency</div>
                            <div class="metric-val">{res_time:.3f}s</div>
                        </div>
                        <div style="text-align: right;">
                            <div class="metric-label">Failures</div>
                            <div class="metric-val">{r['fail_count']}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            fig = go.Figure(go.Indicator(
                mode = "gauge", value = res_time,
                gauge = {
                    'shape': "bullet", 
                    'axis': {'range': [0, 5], 'tickfont': {'size': 10, 'color': '#64748b'}},
                    'bar': {'color': status_color}, 'bgcolor': "#f1f5f9",
                    'steps': [{'range': [0, 1.5], 'color': "rgba(0,0,0,0)"}, {'range': [1.5, 5], 'color': "rgba(239, 68, 68, 0.1)"}],
                    'threshold': {'line': {'color': "#1e293b", 'width': 2}, 'thickness': 0.8, 'value': r.get('max_response_time', 2.0)}
                }
            ))
            
            fig.update_layout(
                height=40, margin=dict(l=5, r=5, t=0, b=20), 
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
            )
            
            # --- FIX: UNIQUE KEY ADDED HERE ---
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"chart_{r['url']}_{idx}")

    time.sleep(refresh_interval)
    st.rerun()
else:
    st.warning("Monitoring Idle. Adjust settings in the sidebar or click Start.")