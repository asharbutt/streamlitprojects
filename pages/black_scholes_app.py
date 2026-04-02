"""
Black-Scholes Pricer & Greeks Dashboard
========================================
Interactive Streamlit app for European option pricing and Greek analysis.

Run with:
    streamlit run app.py
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import bs as bs


# ── Page config ──
st.set_page_config(
    page_title="Black-Scholes Pricer",
    page_icon="📈",
    layout="wide",
)

st.title("Black-Scholes Pricer & Greeks Dashboard")
st.markdown("European option pricing with analytical Greeks under the Black-Scholes framework.")


# ══════════════════════════════════════════════════
# SIDEBAR: INPUT PARAMETERS
# ══════════════════════════════════════════════════

st.sidebar.header("Option Parameters")

S = st.sidebar.number_input("Spot Price (S)", value=100.0, min_value=0.01, step=1.0)
K = st.sidebar.number_input("Strike Price (K)", value=100.0, min_value=0.01, step=1.0)
T = st.sidebar.number_input("Time to Expiry (years)", value=1.0, min_value=0.01, max_value=10.0, step=0.1)
r = st.sidebar.number_input("Risk-Free Rate", value=0.05, min_value=-0.05, max_value=0.30, step=0.005, format="%.3f")
vol = st.sidebar.number_input("Volatility (σ)", value=0.20, min_value=0.01, max_value=2.0, step=0.01, format="%.2f")
q = st.sidebar.number_input("Dividend Yield (q)", value=0.0, min_value=0.0, max_value=0.20, step=0.005, format="%.3f")

option_type = st.sidebar.radio("Option Type", ["call", "put"])

option_price_call = bs.bs_call(S, K, vol, T, r, q)
option_price_put = bs.bs_put(S, K, vol, T, r, q)

# Make an array for all the option prices vs a range of spots

st.markdown("Price vs Spot")

#create a spot range, we do this by moving a certain % away from ATM

spot_range = np.linspace(S*0.5, S*1.5, 300)

#price the calls and puts across the spot range and then plot them

price_call_array = np.array([bs.bs_call(S, K, vol, T, r, q) for S in spot_range])
price_put_array = np.array([bs.bs_put(S, K, vol, T, r, q) for S in spot_range])

st.write("Call price is: ",f"{option_price_call:.4f}", ", Put price is: ",f"{option_price_put:.4f}")

price_fig = make_subplots(rows=1, cols=2,subplot_titles=("Option Price vs Spot", "Delta vs Spot"),horizontal_spacing=0.1,)

price_fig.add_trace(go.Scatter(x=spot_range, y=price_call_array, name="Option Call Price", line=dict(color="blue", width=2)),row=1, col=1,)

price_fig.add_trace(go.Scatter(x=spot_range, y=price_put_array, name="Option Put Price", line=dict(color="red", width=2)),row=1, col=1,)

price_fig.add_vline(x=K, line_dash="dot", line_color="#666", row=1, col=1)

st.plotly_chart(price_fig, use_container_width=True)

#price the greeks across the spot range and then plot them

delta_call_array = np.array([bs.bs_call_delta(S, K, vol, T, r, q) for S in spot_range])
delta_put_array = np.array([bs.bs_put_delta(S, K, vol, T, r, q) for S in spot_range])

gamma_array = np.array([bs.bs_gamma(S, K, vol, T, r, q) for S in spot_range])

greeks_fig = make_subplots(rows=1, cols=2, subplot_titles = ("Options Deltas vs Spot", "Option Gamma vs Spot"), horizontal_spacing=0.1,)

greeks_fig.add_trace(go.Scatter(x=spot_range, y=delta_call_array, name="Option Call Delta", line=dict(color="yellow", width=2)),row=1, col=1,)
greeks_fig.add_trace(go.Scatter(x=spot_range, y=delta_put_array, name="Option Put Delta", line=dict(color="Orange", width=2)),row=1, col=1,)
greeks_fig.add_hline(y=0, line_color="grey",row=1,col=1) #added this to make the y-axis a lot more solid around y=0

greeks_fig.add_trace(go.Scatter(x=spot_range, y=gamma_array, name="Option Gamma", line=dict(color="Green", width=2)),row=1, col=2,)
st.plotly_chart(greeks_fig, use_container_width=True)
