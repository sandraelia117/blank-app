import streamlit as st
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random

# 1. إعدادات الصفحة
st.set_page_config(page_title="Global IoT Data Pipeline", layout="wide")

# --- CSS لتنسيق العناصر الاحترافي ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .status-box {
        padding: 10px; border-radius: 10px; border: 1px solid #e0e0e0;
        background-color: white; text-align: center; font-size: 0.9em;
    }
    .pipeline-arrow { color: #2ecc71; font-size: 20px; display: flex; align-items: center; justify-content: center; }
    .sensor-card {
        background: white; border-radius: 10px; padding: 15px;
        border-top: 4px solid #2ecc71; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px; min-height: 160px;
    }
    .critical-card { border-top: 4px solid #e74c3c !important; }
    .warning-card { border-top: 4px solid #f1c40f !important; }
    .alert-card {
        padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 5px solid; font-size: 0.85em;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. منطق جلب البيانات لـ 10 مدن + IoT
@st.cache_data(ttl=5)
def fetch_global_data():
    # --- محاكاة بيانات IoT (مثلاً حساسات داخلية) ---
    iot_data = [
        {"source": "ESP32_01", "city": "Warehouse-A", "temperature": 18.5, "humidity": 45, "time": datetime.now().strftime("%H:%M:%S")},
        {"source": "ESP32_02", "city": "Server-Room", "temperature": 22.0, "humidity": 35, "time": datetime.now().strftime("%H:%M:%S")}
    ]

    # --- قائمة الـ 10 مدن ---
    cities_urls = {
        "Cairo": "https://www.timeanddate.com/weather/egypt/cairo",
        "London": "https://www.timeanddate.com/weather/uk/london",
        "New York": "https://www.timeanddate.com/weather/usa/new-york",
        "Tokyo": "https://www.timeanddate.com/weather/japan/tokyo",
        "Dubai": "https://www.timeanddate.com/weather/uae/dubai",
        "Paris": "https://www.timeanddate.com/weather/france/paris",
        "Riyadh": "https://www.timeanddate.com/weather/saudi-arabia/riyadh",
        "Sydney": "https://www.timeanddate.com/weather/australia/sydney",
        "Berlin": "https://www.timeanddate.com/weather/germany/berlin",
        "Moscow": "https://www.timeanddate.com/weather/russia/moscow"
    }
    
    scraping_data = []
    for city, url in cities_urls.items():
        try:
            # في بيئة التشغيل الحقيقية نستخدم requests، هنا نضع قيم عشوائية قريبة للواقع للمدن لضمان السرعة
            base_temp = random.randint(10, 38) 
            scraping_data.append({
                "source": "WebScraper",
                "city": city,
                "temperature": round(base_temp + random.uniform(-1, 1), 2),
                "humidity": random.randint(30, 80),
                "time": datetime.now().strftime("%H:%M:%S")
            })
        except: pass

    df = pd.DataFrame(iot_data + scraping_data)
    
    def get_status(t):
        if t > 35 or t < 5: return "CRITICAL"
        elif t > 30 or t < 15: return "WARNING"
        return "NORMAL"
    
    df["status"] = df["temperature"].apply(get_status)
    return df

df = fetch_global_data()

# 3. Pipeline Status (نفس شكل الصورة)
st.subheader("Pipeline Status")
p_cols = st.columns([2, 0.4, 2, 0.4, 2, 0.4, 2, 0.4, 2])
stages = ["Data Simulation", "Ingestion", "ETL Processing", "Analytics", "Dashboard"]
for i, stage in enumerate(stages):
    with p_cols[i*2]:
        st.markdown(f'<div class="status-box"><b>{stage}</b><br><small>🟢 Live</small></div>', unsafe_allow_html=True)
    if i < 4:
        with p_cols[i*2 + 1]:
            st.markdown('<div class="pipeline-arrow">➔</div>', unsafe_allow_html=True)

st.markdown("---")

# 4. Metrics العلوية
m1, m2, m3, m4 = st.columns(4)
m1.metric("Avg Global Temp", f"{round(df['temperature'].mean(), 1)}°C")
m2.metric("Avg Humidity", f"{round(df['humidity'].mean(), 1)}%")
m3.metric("Total Nodes", len(df))
m4.metric("Active Alerts", len(df[df['status'] != 'NORMAL']), delta="Issues Detected", delta_color="inverse")

# 5. Sensor Status (توزيع الـ 12 خانة: 10 مدن + 2 حساس)
st.subheader("🛰️ Global Nodes Status")
for i in range(0, len(df), 4):
    cols = st.columns(4)
    for j, (idx, row) in enumerate(df.iloc[i:i+4].iterrows()):
        card_class = "sensor-card"
        if row['status'] == "CRITICAL": card_class += " critical-card"
        elif row['status'] == "WARNING": card_class += " warning-card"
        
        with cols[j]:
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-size: 0.8em; color: #2ecc71;">● {row['source']}</span>
                    <b style="font-size: 0.7em;">{row['status']}</b>
                </div>
                <h4 style="margin: 5px 0;">{row['city']}</h4>
                <h2 style="margin: 0; color: #2c3e50;">{row['temperature']}°C</h2>
                <p style="margin: 0; font-size: 0.9em;">💧 Humidity: {row['humidity']}%</p>
                <p style="font-size: 0.7em; color: gray; margin-top: 10px;">🕒 {row['time']}</p>
            </div>
            """, unsafe_allow_html=True)

# 6. Charts & Alerts (القسم السفلي)
st.markdown("---")
c_left, c_right = st.columns([1, 2])

with c_left:
    st.subheader("🔔 Active Alerts")
    issues = df[df['status'] != 'NORMAL']
    for _, alert in issues.iterrows():
        color = "#e74c3c" if alert['status'] == "CRITICAL" else "#f1c40f"
        bg = "#fdecea" if alert['status'] == "CRITICAL" else "#fff9e6"
        st.markdown(f'<div class="alert-card" style="background-color: {bg}; border-color: {color}; color: {color};"><b>{alert["status"]}:</b> {alert["city"]} is {alert["temperature"]}°C</div>', unsafe_allow_html=True)
    if issues.empty: st.success("All systems normal")

with c_right:
    st.subheader("📈 Temperature Comparison")
    st.bar_chart(df.set_index("city")["temperature"])

# 7. Recent Readings Table
st.subheader("📋 Detailed Dataset")
def style_status(v):
    color = '#2ecc71' if v == 'NORMAL' else ('#f1c40f' if v == 'WARNING' else '#e74c3c')
    return f'background-color: {color}; color: white'
st.dataframe(df.style.map(style_status, subset=['status']), use_container_width=True)

# التحديث
time.sleep(5)
st.rerun()