import streamlit as st
from scipy.stats import norm
import numpy as np
from datetime import datetime

st.set_page_config(page_title="BSM Option Tool", layout="centered")

st.title("📊 Black-Scholes-Merton (BSM) Tool")

# Toggle for mode
mode = st.radio("Select Mode", ["📈 Option Price Calculator", "🔍 Implied Volatility Calculator"])

# Common Inputs
S = st.number_input("Spot Price (S)", value=19500.0)
K = st.number_input("Strike Price (K)", value=19600.0)

if mode == "📈 Option Price Calculator":
    expiry_date = st.date_input("Expiry Date")
    today = datetime.today().date()
    T = max((expiry_date - today).days / 365, 0.001)
    st.write(f"⏳ Time to Expiry: {T:.4f} years")

    r_percent = st.number_input("Risk-Free Rate (in %)", value=6.0)
    sigma_percent = st.number_input("Volatility (in %)", value=20.0)
    r = r_percent / 100
    sigma = sigma_percent / 100

    option_type = st.selectbox("Option Type", ["Call", "Put"])

    def black_scholes_price(S, K, T, r, sigma, option="Call"):
        d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        if option == "Call":
            price = S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
        else:
            price = K * np.exp(-r*T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        return price, d1, d2

    def calculate_greeks(S, K, T, r, sigma, option, d1, d2):
        delta = norm.cdf(d1) if option == "Call" else -norm.cdf(-d1)
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                - r * K * np.exp(-r*T) * norm.cdf(d2 if option=="Call" else -d2)) / 365
        rho = (K * T * np.exp(-r*T) * norm.cdf(d2) if option=="Call" 
               else -K * T * np.exp(-r*T) * norm.cdf(-d2)) / 100
        return delta, gamma, vega
