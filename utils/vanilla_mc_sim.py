import numpy as np
import scipy.stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import norm

class GBMmodel:
    def __init__(self, r, q, vol, T, increment):
        self.rate = r
        self.divyield = q
        self.vol = vol
        self.maturity = T
        self.dt = increment

    def get_step(self, spot, rv):
        return (self.rate-self.divyield) * self.dt * spot + self.vol * spot * rv * np.sqrt(self.dt)


class arithmetic_model:
    def  __init__(self, r, q, vol, T, increment):
        self.rate = r
        self.divyield = q
        self.vol = vol
        self.maturity = T
        self.dt = increment

    def get_step(self, spot, rv):
        return (self.rate-self.divyield) * self.dt + self.vol * rv * np.sqrt(self.dt)

class monteCarlo:

    def __init__(self, spot_0, r, q, vol, T, increment, num_sims, model):
        self.initial_spot = spot_0
        self.rate = r
        self.divyield = q
        self.vol = vol
        self.maturity = T
        self.dt = increment
        self.num_sims = num_sims
        self.simulated_matrix = np.zeros((self.num_sims*2, int(self.maturity / self.dt)+1))
        self.simulated_matrix[:, 0] = self.initial_spot

        self.process_model = model



    def run_sim(self):
        for i in range(self.num_sims):
            spot_up = self.initial_spot
            spot_down = self.initial_spot
            for j in range(1, int(self.maturity / self.dt)+1):
                z = np.random.normal(0, 1)
                dS = self.process_model.get_step(spot_up, z)
                dS_2 = self.process_model.get_step(spot_down, -z)
                spot_up += dS
                spot_down += dS_2
                self.simulated_matrix [i, j] = spot_up
                self.simulated_matrix[i + self.num_sims, j] = spot_down
        self.final_vector = self.simulated_matrix[:, -1]

def bs_price(type_flag, S,k,t,r,vol,q):
    if type_flag == 'call':
        type_val = 1
    else:
        type_val = -1

    d1 = (np.log(S/k)+(r-q+vol*vol*0.5)*t)/(vol*np.sqrt(t))
    d2 = d1 - vol*np.sqrt(t)

    return type_val*S*norm.cdf(type_val*d1) - type_val*k*np.exp(-r*t)*norm.cdf(type_val*d2)

def price_mc_vanilla(mc_final_vector, strike, option_flag, T,r):
    if option_flag == "call": flag = 1
    else: flag = -1
    payoff_vector = np.zeros(len(mc_final_vector))
    payoff_vector = np.maximum(flag*(mc_final_vector-strike),0)
    price = np.exp(-r*T)*np.mean(payoff_vector)
    return price,payoff_vector
