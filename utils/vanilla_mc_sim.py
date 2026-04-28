import numpy as np
import scipy.stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import norm

class GBMmodel:
    def __init__(self, r, q, vol, T, num_steps):
        self.rate = r
        self.divyield = q
        self.vol = vol
        self.maturity = T
        self.dt = T / num_steps

    def get_step(self, spot_up, spot_down):
        z = np.random.normal(0, 1, size=len(spot_up))
        dS_up = spot_up*np.exp((self.rate-self.divyield - 0.5*self.vol*self.vol)*self.dt + self.vol*np.sqrt(self.dt)*z)
        dS_down = spot_down*np.exp((self.rate-self.divyield - 0.5*self.vol*self.vol)*self.dt + self.vol*np.sqrt(self.dt)*-z)
        return dS_up-spot_up, dS_down-spot_down


class arithmetic_model:
    def  __init__(self, r, q, vol, T, num_steps):
        self.rate = r
        self.divyield = q
        self.vol = vol
        self.maturity = T
        self.dt = T / num_steps

    def get_step(self, spot_up, spot_down):
        z = np.random.normal(0, 1, size=len(spot_up))
        dS = (self.rate - self.divyield) * self.dt + self.vol * z * np.sqrt(self.dt)
        dS_2 = (self.rate - self.divyield) * self.dt + self.vol * -z * np.sqrt(self.dt)
        return dS, dS_2

class monteCarlo:

    def __init__(self, spot_0, r, q, vol_0, T, num_steps, num_sims, model):
        self.initial_spot = spot_0
        self.rate = r
        self.divyield = q
        self.vol = vol_0
        self.maturity = T
        self.dt = T / num_steps
        self.num_sims = num_sims
        self.num_steps = num_steps
        self.simulated_matrix_spot = np.zeros((self.num_sims*2, self.num_steps+1))
        self.simulated_matrix_vol = np.zeros((self.num_sims*2, self.num_steps+1))
        self.simulated_matrix_spot[:, 0] = self.initial_spot
        self.process_model = model

    def run_sim(self):
        spot_up = np.full(self.num_sims ,self.initial_spot)
        spot_down = np.full(self.num_sims ,self.initial_spot)
        for j in range(1, self.num_steps+1):
            dS, dS_2 = self.process_model.get_step(spot_up, spot_down)
            spot_up = spot_up + dS
            spot_down = spot_down + dS_2
            self.simulated_matrix_spot [:self.num_sims, j] = spot_up
            self.simulated_matrix_spot [self.num_sims:, j] = spot_down
        self.simulated_final_spot_vector = self.simulated_matrix_spot[:, -1]

def bs_price(type_flag, S,k,t,r,vol,q):
    if type_flag == 'call':
        type_val = 1
    else:
        type_val = -1

    d1 = (np.log(S/k)+(r-q+vol*vol*0.5)*t)/(vol*np.sqrt(t))
    d2 = d1 - vol*np.sqrt(t)

    return type_val*S*norm.cdf(type_val*d1) - type_val*k*np.exp(-r*t)*norm.cdf(type_val*d2)

def price_mc_vanilla_european(mc_final_vector, strike, option_flag, T,r):
    if option_flag == "call": flag = 1
    else: flag = -1
    payoff_vector = np.zeros(len(mc_final_vector))
    payoff_vector = np.maximum(flag*(mc_final_vector-strike),0)
    price = np.exp(-r*T)*np.mean(payoff_vector)
    return price,payoff_vector

def price_mc_vanilla_american(asset_path_matrix, strike, option_flag, T,r):
    if option_flag == "call": option_flag = 1
    else: option_flag = -1
    
    # We start from the end and work out way backwards
    # Calculate the final payoff first:
    dt = T / (asset_path_matrix.shape[1]-1)
    cashflow_vector = np.maximum(option_flag*(asset_path_matrix[:,-1]-strike),0) # Initialise a vector to keep track of all of the cashflow occurences - given a cashflow can only happen once in a path, we dont need a matrix
    cashflow_timing_vector = np.full(asset_path_matrix.shape[0], 0) # Initialise a vector to keep track of all of the cashflow timing occurences
    cashflow_timing_vector[cashflow_vector>0] = T # where the payoff is positive, set cashflow time

    regression_y = np.zeros(asset_path_matrix.shape[0])# This will store our discounted payoffs for the regression
    regression_x = np.zeros(asset_path_matrix.shape[0])# This will store our x payoffs for the regression

    for i in range(asset_path_matrix.shape[1]-2,0,-1):
        current_payoff = np.maximum(option_flag*(asset_path_matrix[:,i]-strike),0)

        itm_paths = current_payoff > 0

        regression_x = asset_path_matrix[itm_paths,i]
        regression_y = np.exp(-r * dt* (cashflow_timing_vector[itm_paths] - i)) * cashflow_vector[itm_paths]

        # Fit a second degree poly fit curve to the regression:
        z = np.polyfit(regression_x, regression_y, 2)

        exercise_value = regression_x
        continuation_value = np.polyval(z, asset_path_matrix[itm_paths, i])


        # Get the boolean mask of where the path leads to an optimal exercise i.e. exercise > the continuation value we calculated
        optimal_exercise = current_payoff[itm_paths] > continuation_value

        itm_index = np.where(itm_paths==True)[0] # Get the index locations of where we had exercise.
        optimal_index = itm_index[optimal_exercise] # Of those index locations of exercise, we pass which ones we want to keep from the boolean mask

        cashflow_vector[optimal_index] = current_payoff[optimal_index] # Only those that we want to keep will be replaced, the rest will remain the same i.e. the cashflows previously calculated should remain

        cashflow_timing_vector[optimal_index] = i # Add the timing of the cashflow to the vector

    # discount each cashflow back to start
    discounted_cashflow = np.exp(-r*cashflow_timing_vector)*cashflow_vector

    return np.average(discounted_cashflow)
