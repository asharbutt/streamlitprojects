import numpy as np
from scipy.stats import norm

def bs_call(S, K, vol, T, r, q):
    d_1 = (np.log(S / K) + (r - q + 0.5 * vol ** 2) * T) / (vol * np.sqrt(T))
    d_2 = d_1 - vol * np.sqrt(T)
    return S * norm.cdf(d_1) - K * np.exp(-r * T) * norm.cdf(d_2)

def bs_put(S, K, vol, T, r, q):
    d_1 = (np.log(S / K) + (r - q + 0.5 * vol ** 2) * T) / (vol * np.sqrt(T))
    d_2 = d_1 - vol * np.sqrt(T)
    return -S * norm.cdf(-d_1) + K * np.exp(-r * T) * norm.cdf(-d_2)

def bs_call_delta(S, K, vol, T, r, q):
    d_1 = (np.log(S / K) + (r - q + 0.5 * vol ** 2) * T) / (vol * np.sqrt(T))
    return norm.cdf(d_1)

def bs_put_delta(S, K, vol, T, r, q):
    d_1 = (np.log(S / K) + (r - q + 0.5 * vol ** 2) * T) / (vol * np.sqrt(T))
    return -norm.cdf(-d_1)

def bs_gamma(S, K, vol, T, r, q):
    d_1 = (np.log(S / K) + (r - q + 0.5 * vol ** 2) * T) / (vol * np.sqrt(T))
    return 1/(S*vol*np.sqrt(T))*norm.pdf(d_1)
