import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

st.set_page_config(page_title="Smart Money Tracker", layout="wide")

st.title("📊 Smart Money OI Tracker (LIVE)")

# -------------------------
# NSE LIVE DATA FUNCTION
# -------------------------
def get_nse_data():
    try:
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
        }

        session = requests.Session()
        headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "*/*",
    "Referer": "https://www.nseindia.com/",
        }

        response = session.get(url, headers=headers)
        data = response.json()

        records = data["records"]["data"]

        rows = []

        for item in records:
            strike = item["strikePrice"]

            call_oi = item.get("CE", {}).get("openInterest", 0)
            put_oi = item.get("PE", {}).get("openInterest", 0)

            rows.append([strike, call_oi, put_oi])

        df = pd.DataFrame(rows, columns=["Strike", "Call_OI", "Put_OI"])

        nifty_price = data["records"]["underlyingValue"]

        return df, nifty_price

    except:
        return None, None


# -------------------------
# LOAD DATA
# -------------------------
df, nifty_price = get_nse_data()

# -------------------------
# FALLBACK DEMO
# -------------------------
if df is None:
    st.warning("⚠️ Live data blocked, showing demo data")

    strikes = list(range(19500, 20050, 50))

    df = pd.DataFrame({
        "Strike": strikes,
        "Call_OI": np.random.randint(100, 1000, len(strikes)),
        "Put_OI": np.random.randint(100, 1000, len(strikes)),
    })

    nifty_price = 19750

# -------------------------
# PRICE
# -------------------------
st.markdown(f"📍 **Nifty: {nifty_price}**")

# -------------------------
# TREND
# -------------------------
total_call = df["Call_OI"].sum()
total_put = df["Put_OI"].sum()

if total_put > total_call:
    trend = "BULLISH 🟢"
elif total_call > total_put:
    trend = "BEARISH 🔴"
else:
    trend = "SIDEWAYS 🟡"

st.subheader(f"📊 Trend: {trend}")

# -------------------------
# HEATMAP
# -------------------------
st.subheader("🔥 OI Heatmap")

heatmap_df = df.set_index("Strike")[["Call_OI", "Put_OI"]]

fig = px.imshow(
    heatmap_df,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="RdYlGn"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# AUTO SUMMARY
# -------------------------
st.subheader("🤖 Auto Trend Summary")

max_call = df.loc[df["Call_OI"].idxmax()]
max_put = df.loc[df["Put_OI"].idxmax()]

st.write(f"📌 Resistance: {max_call['Strike']}")
st.write(f"📌 Support: {max_put['Strike']}")

if trend == "BULLISH 🟢":
    st.success("Market looks bullish based on OI")
elif trend == "BEARISH 🔴":
    st.error("Market looks bearish based on OI")
else:
    st.warning("Market sideways")

# -------------------------
# TABLE
# -------------------------
st.subheader("📋 Data")

st.dataframe(df, use_container_width=True)
