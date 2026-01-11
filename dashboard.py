import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from qsr_system.strategies.regime_switching import DualMomentum
from qsr_system.analytics.metrics import calculate_sharpe_ratio, calculate_max_drawdown

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="OTPP Quant Engine", layout="wide")
st.title("🛡️ Pension Fund Strategy Simulator")
st.markdown("Test the **Composite Dual Momentum** strategy against different assets and timeframes.")

# --- SIDEBAR: USER INPUTS ---
st.sidebar.header("Strategy Settings")

# 1. Asset Selection
risky_asset = st.sidebar.text_input("Risky Asset (Equities)", value="SPY")
safe_asset = st.sidebar.text_input("Safe Asset (Bonds)", value="TLT")
tickers = [risky_asset, safe_asset]

# 2. Date Range
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2005-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2023-12-31"))

# 3. Parameters
trend_window = st.sidebar.slider("Moving Average Window (Days)", 50, 365, 200)
initial_capital = st.sidebar.number_input("Initial Capital ($)", value=100000)

# --- EXECUTION BUTTON ---
if st.sidebar.button("Run Backtest 🚀"):
    
    # --- 1. DATA LOADING ---
    with st.spinner(f"Downloading data for {tickers}..."):
        try:
            # Download Data
            data = yf.download(tickers, start=start_date, end=end_date, progress=False)
            
            # Handle MultiIndex or simple columns
            if isinstance(data.columns, pd.MultiIndex):
                # Try to get Adj Close, fail over to Close
                try:
                    data = data['Adj Close']
                except KeyError:
                    data = data['Close']
            elif 'Adj Close' in data.columns:
                data = data['Adj Close']
            else:
                data = data['Close']
            
            # Ensure columns map correctly (yfinance sorts alphabetically)
            # We need to guarantee which column is 'Risky' and which is 'Safe'
            if risky_asset not in data.columns or safe_asset not in data.columns:
                st.error("Error: Tickers not found in data. Check spelling.")
                st.stop()
                
            # Rename for the Strategy Class logic (it expects 'SPY' and 'TLT' logic)
            # Or we can update the class, but renaming is easier for now:
            data = data.rename(columns={risky_asset: 'SPY', safe_asset: 'TLT'})
            
            data = data.ffill().dropna()
            
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.stop()

    # --- 2. RUN STRATEGY ---
    # Setup
    daily_rets = data.pct_change()
    
    # Initialize Strategy with USER INPUT window
    strategy = DualMomentum(trend_window=trend_window)
    
    # Generate Signals
    signals = strategy.generate_signals(data)
    aligned_signals = signals.shift(1).fillna(0.0)
    
    # Calculate Strategy Returns
    # Weight_1 * Risky + Weight_2 * Safe + Cash (implied 0)
    strategy_returns = (aligned_signals['spy_weight'] * daily_rets['SPY']) + \
                       (aligned_signals['tlt_weight'] * daily_rets['TLT'])
    
    # Calculate Benchmark (60/40) using the CHOSEN assets
    benchmark_returns = (0.60 * daily_rets['SPY']) + (0.40 * daily_rets['TLT'])
    
    # Equity Curves
    portfolio_value = initial_capital * (1 + strategy_returns).cumprod()
    benchmark_value = initial_capital * (1 + benchmark_returns).cumprod()
    
    # --- 3. METRICS ---
    my_sharpe = calculate_sharpe_ratio(strategy_returns)
    bench_sharpe = calculate_sharpe_ratio(benchmark_returns)
    my_dd = calculate_max_drawdown(portfolio_value)
    bench_dd = calculate_max_drawdown(benchmark_value)
    
    # --- 4. DISPLAY RESULTS ---
    
    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Strategy Return", f"{(portfolio_value.iloc[-1]/initial_capital - 1):.1%}")
    col2.metric("Max Drawdown", f"{my_dd:.1%}", delta=f"{my_dd - bench_dd:.1%}", delta_color="inverse")
    col3.metric("Sharpe Ratio", f"{my_sharpe:.2f}")
    col4.metric("Benchmark Sharpe", f"{bench_sharpe:.2f}")
    
    # Chart
    st.subheader("Equity Curve")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(portfolio_value, label=f"Strategy ({risky_asset}/{safe_asset})", color='#1f77b4', lw=2)
    ax.plot(benchmark_value, label=f"Benchmark (60/40)", color='gray', ls='--', alpha=0.6)
    
    # Annotate 2022 if in range
    if pd.Timestamp('2022-06-01') in portfolio_value.index:
         ax.annotate('2022 Cash Safety', 
                     xy=(pd.Timestamp('2022-06-01'), portfolio_value.asof('2022-06-01')), 
                     xytext=(pd.Timestamp('2020-01-01'), portfolio_value.asof('2022-06-01') + (initial_capital*0.2)),
                     arrowprops=dict(facecolor='black', shrink=0.05))

    ax.set_title("Portfolio Performance")
    ax.set_ylabel("Value ($)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)
    
    # Data Table
    with st.expander("See Raw Data"):
        st.write(data.tail())