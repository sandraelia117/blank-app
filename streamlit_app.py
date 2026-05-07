import streamlit as st
import pandas as pd
import requests
import random
from datetime import datetime
import time

st.set_page_config(page_title="Real-Time IoT Weather Dashboard", layout="wide")

st.title("🌍 Real-Time IoT Weather Dashboard")

# =========================
# WEATHER SOURCES (Scraping API)
# =========================
cities = {
    "Cairo": "https://wttr.in/Cairo?format=j1",
    "London": "https://wttr.in/London?format=j1",
    "New York": "https://wttr.in/New+York?format=j1",
    "Paris": "https://wttr.in/Paris?format=j1"
}

data = []

for city, url in cities.items():
    try:
        res = requests.get(url, timeout=5)
        weather = res.json()

        temp = float(weather["current_condition"][0]["temp_C"])
        humidity = float(weather["current_condition"][0]["humidity"])

        # simulation slight change (streaming feel)
        temp += random.uniform(-1, 1)
        humidity += random.uniform(-2, 2)

        # status logic
        if temp > 35:
            status = "CRITICAL"
        elif temp > 30:
            status = "WARNING"
        else:
            status = "NORMAL"

        data.append({
            "city": city,
            "temperature": round(temp, 2),
            "humidity": round(humidity, 2),
            "status": status,
            "time": datetime.now().strftime("%H:%M:%S")
        })

    except:
        data.append({
            "city": city,
            "temperature": 0,
            "humidity": 0,
            "status": "ERROR",
            "time": datetime.now().strftime("%H:%M:%S")
        })

df = pd.DataFrame(data)

# =========================
# PIPELINE STATUS
# =========================
st.subheader("⚡ Pipeline Status")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Data Simulation", "4 Sensors Active")
c2.metric("Ingestion", f"{len(df)} Readings")
c3.metric("ETL Alerts", len(df[df["status"] != "NORMAL"]))
c4.metric("Dashboard", "LIVE")

st.markdown("---")

# =========================
# GLOBAL METRICS
# =========================
st.subheader("📈 Global Metrics")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Avg Temperature", f"{df['temperature'].mean():.2f} °C")
m2.metric("Avg Humidity", f"{df['humidity'].mean():.2f} %")
m3.metric("Total Sensors", len(df))
m4.metric(
    "Anomaly Rate",
    f"{(len(df[df['status']!='NORMAL'])/len(df)*100):.1f}%"
)

st.markdown("---")

# =========================
# SENSOR STATUS
# =========================
st.subheader("🛰 Sensor Status")

cols = st.columns(len(df))

for i, row in df.iterrows():
    with cols[i]:

        if row["status"] == "CRITICAL":
            st.error(f"""
{row['city']}

🌡 {row['temperature']} °C  
💧 {row['humidity']} %  
🚨 {row['status']}  
🕒 {row['time']}
""")

        elif row["status"] == "WARNING":
            st.warning(f"""
{row['city']}

🌡 {row['temperature']} °C  
💧 {row['humidity']} %  
⚠ {row['status']}  
🕒 {row['time']}
""")

        else:
            st.success(f"""
{row['city']}

🌡 {row['temperature']} °C  
💧 {row['humidity']} %  
✅ {row['status']}  
🕒 {row['time']}
""")

st.markdown("---")

# =========================
# LIVE CHART
# =========================
st.subheader("📊 Live Weather Chart")

chart_df = df.melt(
    id_vars=["city"],
    value_vars=["temperature", "humidity"],
    var_name="metric",
    value_name="value"
)

st.bar_chart(chart_df, x="city", y="value")

# =========================
# ALERTS
# =========================
st.subheader("🚨 Alerts")

alerts = df[df["status"] != "NORMAL"]

if alerts.empty:
    st.success("✅ No Active Alerts")
else:
    for _, row in alerts.iterrows():
        st.warning(f"{row['city']} → {row['status']}")

# =========================
# TABLE
# =========================
st.subheader("📋 Latest Weather Data")
st.dataframe(df, use_container_width=True)

st.caption("🔄 Auto refresh every 5 seconds")

# =========================
# AUTO REFRESH (IMPORTANT)
# =========================
time.sleep(5)
st.rerun()