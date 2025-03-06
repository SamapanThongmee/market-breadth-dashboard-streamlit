import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import datetime as dt
import numpy as np
import math

# Set Streamlit page config
st.set_page_config(page_title="SET Index Market Breadth", layout="wide")

# Public Google Sheet URL
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1w4tM7NxXL2PFm95V0QW3H3WJ1togISgxPUKZyTLnv4c/edit#gid=0"

@st.cache_data(ttl=600)
def fetch_google_sheet_data(sheet_url):
    sheet_id = sheet_url.split("/d/")[1].split("/")[0]
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
    df = pd.read_csv(csv_url)
    return df

st.sidebar.header("Market Breadth Dashboard")
if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()

# Fetch and preprocess data
df = fetch_google_sheet_data(GOOGLE_SHEET_URL)
df["Date"] = pd.to_datetime(df["Date"])
numeric_cols = ["Open", "High", "Low", "Close", "MA20", "MA60", "MA200", 
                "McClellan_Oscillator", "McClellan_Summation_Index"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Generate date breaks for missing dates
dt_all = pd.date_range(start=df['Date'].iloc[0], end=df['Date'].iloc[-1])
dt_obs = [d for d in pd.to_datetime(df['Date'])]
dt_breaks = [d.strftime("%Y-%m-%d") for d in dt_all if d not in dt_obs]

# Create subplots with modified spacing and row heights
fig1 = make_subplots(
    rows=4, cols=1, shared_xaxes=True,
    vertical_spacing=0.025,
    row_heights=[0.4, 0.3, 0.3, 0.3]
)

# Row 1: Candlestick Chart
fig1.add_trace(go.Candlestick(
    x=df['Date'],
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    name='SET Index'
), row=1, col=1)

# Row 2: Moving Averages
fig1.add_trace(go.Scatter(x=df['Date'], y=df['MA20'], mode='lines', name='MA20',
                          line=dict(color='#69DC5B', width=1.0)), row=2, col=1)
fig1.add_trace(go.Scatter(x=df['Date'], y=df['MA60'], mode='lines', name='MA60',
                          line=dict(color='#526DFF', width=1.5)), row=2, col=1)
fig1.add_trace(go.Scatter(x=df['Date'], y=df['MA200'], mode='lines', name='MA200',
                          line=dict(color='#E24C4C', width=2.0)), row=2, col=1)

# Add horizontal lines to the moving averages subplot (row 2)
for y, color in zip([90, 80, 50, 20, 10],
                    ['#2ECC71', '#82E0AA', '#CCD1D1', '#F1948A', '#E74C3C']):
    fig1.add_hline(y=y, line_dash="dot", line=dict(color=color, width=0.75), row=2, col=1)

# Row 3: McClellan Oscillator
fig1.add_trace(go.Scatter(x=df['Date'], y=df['McClellan_Oscillator'], mode='lines',
                          name='McClellan Oscillator', line=dict(color='#69DC5B', width=2.0)), row=3, col=1)
# Add horizontal lines to the oscillator subplot (row 3)
for y, color in zip([50, 25, 0, -25, -50],
                    ['#2ECC71', '#82E0AA', '#CCD1D1', '#F1948A', '#E74C3C']):
    fig1.add_hline(y=y, line_dash="dot", line=dict(color=color, width=0.75), row=3, col=1)

# Row 4: McClellan Summation Index
fig1.add_trace(go.Scatter(x=df['Date'], y=df['McClellan_Summation_Index'], mode='lines',
                          name='McClellan Summation Index', line=dict(color='#27AE60', width=2.0)), row=4, col=1)
# Add a 20-day rolling average line (dotted) for the summation index
rolling_sum = df['McClellan_Summation_Index'].rolling(window=20).mean()
fig1.add_trace(go.Scatter(x=df['Date'], y=rolling_sum, mode='lines', name='Rolling Mean',
                          line=dict(color='#FF85E3', width=1.5, dash="dot")), row=4, col=1)

# Update x-axis for missing dates on all subplots
for i in range(1, 5):
    fig1.update_xaxes(rangebreaks=[dict(values=dt_breaks)], row=i, col=1)

# Dynamic Y-axis scaling for the candlestick chart (row 1)
interval = 100
min_val = math.floor(math.ceil(df.tail(365)['Low'].min()) / interval) * interval
max_val = math.ceil(df.tail(365)['High'].max() / interval) * interval
fig1.update_yaxes(
    tickmode='array',
    tickvals=list(range(min_val, max_val + interval, interval)),
    title_text="SET Index",
    row=1, col=1
)

# Update y-axis for Moving Averages (row 2)
fig1.update_yaxes(
    tickmode='array',
    tickvals=[0, 25, 50, 75, 100],
    ticktext=['0', '25', '50', '75', '100'],
    range=[0, 100],
    title_text="Moving Averages",
    row=2, col=1
)

# Update y-axis for McClellan Oscillator (row 3)
fig1.update_yaxes(
    tickmode='array',
    tickvals=[-75, -50, -25, 0, 25, 50, 75],
    ticktext=['-75', '-50', '-25', '0', '25', '50', '75'],
    range=[-75, 75],
    title_text="McClellan Oscillator",
    row=3, col=1
)

# Update y-axis for McClellan Summation Index (row 4)
fig1.update_yaxes(
    title_text="McClellan Summation Index",
    row=4, col=1
)

# Define x-axis range if desired
start_date = dt.datetime.today() - dt.timedelta(days=182)
end_date = dt.datetime.today() + dt.timedelta(hours=7)
fig1.update_layout(
    height=900,
    width=1200,
    plot_bgcolor="#F7F9F9",
    title='SET Index and Market Breadth Indicators',
    title_font=dict(size=16, family='Arial', color='#566573'),
    showlegend=False,  # Disable global legend since we use annotations
    xaxis_rangeslider_visible=False,
    xaxis_range=[start_date, end_date],
    annotations=[
        # Annotation for Candlestick (Row 1)
        dict(
            x=1.0, y=1,
            xref='paper', yref='paper',
            text="SET Index",
            showarrow=False,
            font=dict(size=12, color="black"),
            bgcolor="white", bordercolor="#b2babb", borderwidth=0.5
        ),
        # Annotation for Moving Averages (Row 2)
        dict(
            x=1, y=0.688,
            xref='paper', yref='paper',
            text="<span style='color:#69DC5B'>% Stocks Above MA20d</span><br>"
                 "<span style='color:#526DFF'>% Stocks Above MA60d</span><br>"
                 "<span style='color:#E24C4C'>% Stocks Above MA200d</span>",
            showarrow=False,
            font=dict(size=12),
            align="left",
            bgcolor="white", bordercolor="#b2babb", borderwidth=0.5
        ),
        # Annotation for McClellan Oscillator (Row 3)
        dict(
            x=1, y=0.44,
            xref='paper', yref='paper',
            text="<span style='color:#69DC5B'>McClellan Oscillator</span>",
            showarrow=False,
            font=dict(size=12),
            align="left",
            bgcolor="white", bordercolor="#b2babb", borderwidth=0.5
        ),
        # Annotation for McClellan Summation Index (Row 4)
        dict(
            x=1, y=0.19,
            xref='paper', yref='paper',
            text="<span style='color:#27AE60'>McClellan Summation Index</span>",
            showarrow=False,
            font=dict(size=12),
            align="left",
            bgcolor="white", bordercolor="#b2babb", borderwidth=0.5
        )
    ]
)

st.subheader("📊 SET Index Market Breadth Dashboard")
import streamlit as st

st.markdown(
    '<p style="font-size:12px;">'
    '<span style="color:#4CAF50;">% Stocks Above 20d</span> represents the percentage of stocks in the SET Index with a closing price above their 20-day simple moving average.<br>'
    '<span style="color:#526DFF;">% Stocks Above 60d</span> represents the percentage of stocks in the SET Index with a closing price above their 60-day simple moving average.<br>'
    '<span style="color:#E24C4C;">% Stocks Above 200d</span> represents the percentage of stocks in the SET Index with a closing price above their 200-day simple moving average.'
    '</p>', 
    unsafe_allow_html=True
)


st.plotly_chart(fig1, use_container_width=True)
st.sidebar.write("Created by Samapan Thongmee")
