import streamlit as st
import requests
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("📊 Smart Money Tracker (Stable)")

@st.cache_data(ttl=60)
def get_data():
    try:
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }

        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)

        response = session.get(url, headers=headers, timeout=5)

        if response.status_code != 200:
            raise Exception("API blocked")

        data = response.json()

        records = data['records']['data']

        rows = []
        for i in records:
            if "CE" in i and "PE" in i:
                rows.append({
                    "Strike": i['strikePrice'],
                    "Call_OI": i['CE']['openInterest'],
                    "Put_OI": i['PE']['openInterest'],
                    "Call_Chg": i['CE']['changeinOpenInterest'],
                    "Put_Chg": i['PE']['changeinOpenInterest']
                })

        df = pd.DataFrame(rows)
        nifty = data['records']['underlyingValue']

        return df, nifty

    except:
        # fallback dummy data (IMPORTANT)
        st.warning("⚠️ Live data blocked, showing demo data")

        strikes = list(range(19500, 20000, 50))
        df = pd.DataFrame({
            "Strike": strikes,
            "Call_OI": np.random.randint(10000, 50000, len(strikes)),
            "Put_OI": np.random.randint(10000, 50000, len(strikes)),
            "Call_Chg": np.random.randint(-5000, 5000, len(strikes)),
            "Put_Chg": np.random.randint(-5000, 5000, len(strikes))
        })

        return df, 19750


df, nifty = get_data()

st.subheader(f"📍 Nifty: {nifty}")

df['OI_Diff'] = df['Put_Chg'] - df['Call_Chg']

# TREND
trend = "SIDEWAYS"
if df['OI_Diff'].sum() > 0:
    trend = "BULLISH 🟢"
elif df['OI_Diff'].sum() < 0:
    trend = "BEARISH 🔴"

st.subheader(f"📊 Trend: {trend}")

# ALERT
if df['OI_Diff'].sum() > 50000:
    st.success("🚀 Bullish Build-up")
elif df['OI_Diff'].sum() < -50000:
    st.error("🔻 Bearish Build-up")

# HEATMAP
st.subheader("🔥 OI Heatmap")

def color(val):
    return "background-color: green" if val > 0 else "background-color: red"

st.dataframe(df.style.applymap(color, subset=["OI_Diff"]))
