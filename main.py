import streamlit as st
import pandas as pd
import plotly.graph_objects as go
# Data visualization
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
import plotly
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.subplots
import datetime as dt
import numpy as np
import math

# Set Streamlit page config
st.set_page_config(page_title="Stock Market Breadth Dashboard", layout="wide")

# Public Google Sheet URL
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1w4tM7NxXL2PFm95V0QW3H3WJ1togISgxPUKZyTLnv4c/edit#gid=0"

# Function to fetch data from Google Sheets
@st.cache_data(ttl=600)
def fetch_google_sheet_data(sheet_url):
    sheet_id = sheet_url.split("/d/")[1].split("/")[0]  # Extract Sheet ID
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
    df = pd.read_csv(csv_url)
    return df

# Sidebar refresh button
st.sidebar.header("Market Breadth Dashboard")
if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()

# Fetch data
df = fetch_google_sheet_data(GOOGLE_SHEET_URL)

# Convert date column and ensure numeric types
df["Date"] = pd.to_datetime(df["Date"])
numeric_cols = ["Open", "High", "Low", "Close", "MA20", "MA60", "MA200", 
                "McClellan_Oscillator", "McClellan_Summation_Index"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Generate date range and missing date breaks
dt_all = pd.date_range(start=df['Date'].iloc[0], end=df['Date'].iloc[-1])
dt_obs = [d for d in pd.to_datetime(df['Date'])]
dt_breaks = [d.strftime("%Y-%m-%d") for d in dt_all if d not in dt_obs]

# Initialize Plotly Figure
fig1 = plotly.subplots.make_subplots(rows=4, cols=1, shared_xaxes=True,
                                     vertical_spacing=0.025,
                                     row_heights=[0.4, 0.3, 0.3, 0.3])

# Candlestick Chart
fig1.add_trace(go.Candlestick(x=df['Date'],
                              open=df['Open'],
                              high=df['High'],
                              low=df['Low'],
                              close=df['Close'],
                              name='Stock Index'),
               row=1, col=1)

# Moving Averages
fig1.add_trace(go.Scatter(x=df['Date'], y=df['MA20'], mode='lines', name='MA20', line=dict(color='#69DC5B', width=1.0)), row=2, col=1)
fig1.add_trace(go.Scatter(x=df['Date'], y=df['MA60'], mode='lines', name='MA60', line=dict(color='#526DFF', width=1.5)), row=2, col=1)
fig1.add_trace(go.Scatter(x=df['Date'], y=df['MA200'], mode='lines', name='MA200', line=dict(color='#E24C4C', width=2.0)), row=2, col=1)

# McClellan Oscillator
fig1.add_trace(go.Scatter(x=df['Date'], y=df['McClellan_Oscillator'], mode='lines', name='McClellan Oscillator', line=dict(color='#69DC5B', width=2.0)), row=3, col=1)

# McClellan Summation Index
fig1.add_trace(go.Scatter(x=df['Date'], y=df['McClellan_Summation_Index'], mode='lines', name='McClellan Summation Index', line=dict(color='#27AE60', width=2.0)), row=4, col=1)

# Update X-axis for missing dates
fig1.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

# Dynamic Y-axis Scaling
interval = 100
min_val = math.floor(math.ceil(df.tail(365)['Low'].min()) / interval) * interval
max_val = math.ceil(df.tail(365)['High'].max() / interval) * interval
fig1.update_yaxes(tickmode='array', tickvals=list(range(min_val, max_val + interval, interval)), row=1, col=1)

# Layout Customization
fig1.update_layout(height=900, width=1200,
                   plot_bgcolor="#F7F9F9",
                   title='Stock Index and Market Breadth Indicators',
                   title_font=dict(size=16, family='Arial', color='#566573'),
                   showlegend=True)

# Streamlit Plot
st.subheader("📊 Market Breadth Dashboard")
st.plotly_chart(fig1, use_container_width=True)

# Footer
st.sidebar.write("Powered by Google Sheets & Streamlit")
