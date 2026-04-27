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
from utils import vanilla_mc_sim as mc


# ── Page config ──
st.set_page_config(
    page_title="Black-Scholes Pricer",
    page_icon="📈",
    layout="wide",
)

st.title("Monte Carlo Simulator")
st.markdown("Vanilla European Option Pricer using MC")

st.markdown("We use Antithetic variables to increase the number of simulations at a reduced time i.e. for every run and standard normal value generated, the negative of that value is taken to generate another path, hence you will see N*2 number of simulations in the convergence plot")
# ══════════════════════════════════════════════════
# SIDEBAR: INPUT PARAMETERS
# ══════════════════════════════════════════════════

st.sidebar.header("Simulation Parameters")

S = st.sidebar.number_input("Spot Price (S)", value=100.0, min_value=0.01, step=1.0)
K = st.sidebar.number_input("Strike Price (K)", value=100.0, min_value=0.01, step=1.0)
T = st.sidebar.number_input("Time to Expiry (years)", value=1.0, min_value=0.01, max_value=10.0, step=0.1)
r = st.sidebar.number_input("Risk-Free Rate", value=0.05, min_value=-0.05, max_value=0.30, step=0.005, format="%.3f")
vol = st.sidebar.number_input("Volatility (σ)", value=0.20, min_value=0.01, max_value=2.0, step=0.01, format="%.2f")
q = st.sidebar.number_input("Dividend Yield (q)", value=0.0, min_value=0.0, max_value=0.20, step=0.005, format="%.3f")
num_sims = int(st.sidebar.number_input("Number of Simulations", value=1, min_value=1, max_value=1000000000000, step=1))
num_steps = int(st.sidebar.number_input("Number of Steps", value=1, min_value=1, max_value=100000.0, step=1))
process_dropdown = st.sidebar.selectbox("Asset process", ( "Arithmetic Brownian Motion", "Geometric  Brownian Motion"))
option_type = st.sidebar.radio("Option Type", ["call", "put"])

#simulate the process paths

if process_dropdown == "Arithmetic Brownian Motion":
    process_model = mc.arithmetic_model(r,q,vol,T,num_steps)
elif process_dropdown == "Geometric  Brownian Motion":
    process_model = mc.GBMmodel(r,q,vol,T,num_steps)  #we create an object for the process model we want (possibly change this to something else using a dropdown int he future)
simulation = mc.monteCarlo(S,r,q,vol, T,num_steps,num_sims, process_model)
simulation.run_sim()

option_price, payoff_vector = mc.price_mc_vanilla(simulation.final_vector, K, option_type, T, r)

convergence_vector = np.zeros(num_sims * 2)
convergence_vector = np.cumsum(payoff_vector) / np.arange(1, len(payoff_vector) + 1, 1)

bs_value = mc.bs_price(option_type, S,K,T,r,vol,q)

st.write("The option price is: ", f"{option_price:.4f}")

fig = make_subplots(rows=2, cols=2,subplot_titles=("Simulated Paths (Visualisation limited to 2000 paths)", "Distribution of terminal spot price", "Convergence of simulated average payoff to BS price"),horizontal_spacing=0,)
if numsims >= 2000:
    for i in range(2000):
        fig.add_trace(go.Scatter(y=simulation.simulated_matrix[i,:], mode="lines",name=f"path {i}"), row=1, col=1)
else:
    for i in range(numsims):
        fig.add_trace(go.Scatter(y=simulation.simulated_matrix[i,:], mode="lines",name=f"path {i}"), row=1, col=1)
fig.add_trace(go.Histogram(y=simulation.simulated_matrix[:,-1],nbinsy=150),row=1,col=2)

fig.add_trace(go.Scatter(y=convergence_vector, mode="lines",name=f"path {i}"), row=2, col=1)
fig.add_hline(y=bs_value, line_color="grey",row=2,col=1) #added this to make the y-axis a lot more solid around y=0


fig.update_layout(showlegend=False)    
fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, row=1, col=2)

st.plotly_chart(fig, width="stretch", height=750)
