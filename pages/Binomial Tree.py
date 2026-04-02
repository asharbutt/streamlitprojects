from utils import binomial as bt

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ── Page config ──
st.set_page_config(
    page_title="Equity Binomial Tree Pricer",
    page_icon="📈",
    layout="wide",
)

st.title("Equity Binomial Tree Pricer")
st.markdown("European and American Equity Option pricing using binomial tree method")
st.write("The option price is: ", f"{option_price:.4f}")
# ══════════════════════════
# SIDEBAR: INPUT PARAMETERS
# ══════════════════════════

st.sidebar.header("Input Parameters")

S = st.sidebar.number_input("Spot Price (S)", value=100.0, min_value=0.01, step=1.0)
K = st.sidebar.number_input("Strike Price (K)", value=100.0, min_value=0.01, step=1.0)
T = st.sidebar.number_input("Time to Expiry (years)", value=1.0, min_value=0.01, max_value=10.0, step=0.1)
r = st.sidebar.number_input("Risk-Free Rate", value=0.05, min_value=-0.05, max_value=0.30, step=0.005, format="%.3f")
vol = st.sidebar.number_input("Volatility (σ)", value=0.20, min_value=0.01, max_value=2.0, step=0.01, format="%.2f")
q = st.sidebar.number_input("Dividend Yield (q)", value=0.0, min_value=0.0, max_value=0.20, step=0.005, format="%.3f")
steps = int(st.sidebar.number_input("Number of Steps", value=1, min_value=1, max_value=1000000000000, step=1))
option_type = st.sidebar.radio("Option Type", ["call", "put"])
exercise_type = st.sidebar.radio("Option Type", ["European", "American"])


p = bt.european_binomial(steps,vol,S,K,T, option_type,r)
option_price = p.run_tree()

fig = bt.plot_binomial_tree(p)
st.plotly_chart(fig)

