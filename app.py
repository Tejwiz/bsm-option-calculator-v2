# Toggle at the top
mode = st.radio("Select Mode", ["Premium Calculator", "Implied Volatility Calculator"])

# Common Inputs
S = st.number_input("Spot Price (S)", value=19500.0)
K = st.number_input("Strike Price (K)", value=19600.0)
expiry_date = st.date_input("Expiry Date")
r_percent = st.number_input("Risk-Free Rate (in %)", value=6.0)
vol_percent = st.number_input("Volatility (in %)", value=20.0)

# Auto calculate time to expiry
from datetime import date
T = max((expiry_date - date.today()).days / 365, 0.0001)  # Avoid division by zero
r = r_percent / 100
sigma = vol_percent / 100

# Dropdown for Call/Put
option_type = st.selectbox("Option Type", ["Call", "Put"])

# MODE: Premium Calculation
if mode == "Premium Calculator":
    if st.button("Calculate Option Price"):
        # BSM Pricing
        d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        if option_type == "Call":
            price = S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
        else:
            price = K * np.exp(-r*T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        st.success(f"💰 {option_type} Option Price: ₹ {price:.2f}")
        
        # Greeks
        delta = norm.cdf(d1) if option_type == "Call" else -norm.cdf(-d1)
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100
        theta = (
            (-S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
            - r * K * np.exp(-r*T) * norm.cdf(d2 if option_type == "Call" else -d2)
        ) / 365
        rho = (K * T * np.exp(-r*T) * norm.cdf(d2 if option_type == "Call" else -d2)) / 100
        
        st.markdown("### Option Greeks")
        st.write(f"**Delta:** {delta:.4f}")
        st.write(f"**Gamma:** {gamma:.4f}")
        st.write(f"**Vega:** {vega:.4f}")
        st.write(f"**Theta:** {theta:.4f}")
        st.write(f"**Rho:** {rho:.4f}")

# MODE: Implied Volatility Calculation
else:
    market_price = st.number_input("Market Option Price (₹)", value=250.0)
    if st.button("Calculate Implied Volatility"):
        def bs_price(vol):
            d1 = (np.log(S/K) + (r + vol**2/2)*T) / (vol * np.sqrt(T))
            d2 = d1 - vol * np.sqrt(T)
            if option_type == "Call":
                return S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
            else:
                return K * np.exp(-r*T) * norm.cdf(-d2) - S * norm.cdf(-d1)

        # Newton-Raphson method
        iv = 0.2  # initial guess
        for _ in range(100):
            price = bs_price(iv)
            vega = S * norm.pdf((np.log(S/K) + (r + iv**2/2)*T) / (iv * np.sqrt(T))) * np.sqrt(T)
            diff = price - market_price
            if abs(diff) < 1e-5:
                break
            iv -= diff / vega

        st.success(f"📊 Implied Volatility: {iv*100:.2f} %")
