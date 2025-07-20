import streamlit as st
from scipy.stats import norm
import numpy as np
from datetime import date

st.set_page_config(page_title="BSM Option Calculator", layout="centered")

st.title("📈 Black-Scholes Option Pricing Calculator")

# Inputs
S = st.number_input("Spot Price (S)", value=19500.0)
K = st.number_input("Strike Price (K)", value=19600.0)
expiry = st.date_input("Expiry Date", value=date(2025, 8, 30))
today = date.today()
T = (expiry - today).days / 365

r_percent = st.number_input("Risk-Free Rate (r) [%]", value=6.0)
σ_percent = st.number_input("Volatility (σ) [%]", value=20.0)

option_type = st.selectbox("Option Type", ["Call", "Put"])

# Convert to decimal
r = r_percent / 100
σ = σ_percent / 100

# BSM Formulas
def black_scholes(S, K, T, r, sigma, option_type="Call"):
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == "Call":
        price = S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r*T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return price, d1, d2

def option_greeks(S, K, T, r, sigma, d1, d2, option_type):
    delta = norm.cdf(d1) if option_type == "Call" else -norm.cdf(-d1)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    theta_call = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))) - r * K * np.exp(-r*T) * norm.cdf(d2)
    theta_put = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))) + r * K * np.exp(-r*T) * norm.cdf(-d2)
    theta = theta_call if option_type == "Call" else theta_put
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100  # per 1% change
    rho_call = K * T * np.exp(-r*T) * norm.cdf(d2) / 100
    rho_put = -K * T * np.exp(-r*T) * norm.cdf(-d2) / 100
    rho = rho_call if option_type == "Call" else rho_put

    return {
        "Delta": delta,
        "Gamma": gamma,
        "Theta": theta,
        "Vega": vega,
        "Rho": rho
    }

# Calculation
if st.button("Calculate Option Price"):
    if T <= 0:
        st.error("❌ Expiry date must be in the future.")
    else:
        price, d1, d2 = black_scholes(S, K, T, r, σ, option_type)
        st.success(f"💰 {option_type} Option Price: ₹ {price:.2f}")

        greeks = option_greeks(S, K, T, r, σ, d1, d2, option_type)
        st.subheader("🧮 Option Greeks")
        for greek, value in greeks.items():
            st.write(f"**{greek}**: {value:.4f}")
