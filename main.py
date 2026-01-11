import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from qsr_system.strategies.regime_switching import DualMomentum 
from qsr_system.analytics.metrics import calculate_sharpe_ratio, calculate_max_drawdown

def load_multi_asset_data(tickers=['SPY', 'TLT'], start_date='2005-01-01', end_date='2023-01-01'):
    """
    Downloads multiple tickers and combines them into one DataFrame.
    """
    print(f"--- ⬇️ Downloading {tickers} ---")
    # Note: For recent yfinance versions, we might need to handle MultiIndex columns manually
    # if it returns a complex structure.
    data = yf.download(tickers, start=start_date, end=end_date, progress=False)
    
    # If 'Close' is a MultiIndex (e.g. Price -> Ticker), extract it safely
    if isinstance(data.columns, pd.MultiIndex):
        # We prefer 'Adj Close' for total return calculations
        try:
            data = data['Adj Close']
        except KeyError:
            data = data['Close']
    elif 'Adj Close' in data.columns:
        # If flat index but has Adj Close
        data = data['Adj Close']
    else:
        # Fallback
        data = data['Close']

    # Clean data (fill missing values)
    data = data.ffill().dropna()
    return data

def run_regime_backtest(data):
    print("--- 🚀 Starting Multi-Asset Engine ---")
    
    # 1. SETUP VARIABLES (Move this to the top!)
    initial_capital = 100000.0
    daily_rets = data.pct_change()

    # 2. BENCHMARK CALCULATION (Now this works because daily_rets exists)
    # 60% SPY / 40% TLT Benchmark
    benchmark_returns = (0.60 * daily_rets['SPY']) + (0.40 * daily_rets['TLT'])
    benchmark_value = initial_capital * (1 + benchmark_returns).cumprod()
    
    # 3. STRATEGY EXECUTION
    # 1. Initialize Strategy
    strategy = DualMomentum(trend_window=200)
    
    # 2. Get Signals (Now returns two columns: spy_weight and tlt_weight)
    signals = strategy.generate_signals(data)
    
    # Shift signals to avoid look-ahead bias
    aligned_signals = signals.shift(1).fillna(0.0)
    
    # 3. Calculate Portfolio Return (Vectorized)
    # Return = (Weight_SPY * Ret_SPY) + (Weight_TLT * Ret_TLT) + (Weight_Cash * 0)
    strategy_returns = (aligned_signals['spy_weight'] * daily_rets['SPY']) + \
                       (aligned_signals['tlt_weight'] * daily_rets['TLT'])
    
    # Construct Equity Curve
    portfolio_value = initial_capital * (1 + strategy_returns).cumprod()
    
    # 4. METRICS & OUTPUT
    my_sharpe = calculate_sharpe_ratio(strategy_returns)
    bench_sharpe = calculate_sharpe_ratio(benchmark_returns)
    
    my_dd = calculate_max_drawdown(portfolio_value)
    bench_dd = calculate_max_drawdown(benchmark_value)

    print(f"\n[Performance Report]")
    print(f"Strategy Sharpe: {my_sharpe:.2f} | Max Drawdown: {my_dd:.2%}")
    print(f"Benchmark Sharpe: {bench_sharpe:.2f} | Max Drawdown: {bench_dd:.2%}")

    # 5. PLOTTING
    plt.figure(figsize=(12, 6))
    
    # Plot Strategy & Benchmark
    plt.plot(portfolio_value, label='Regime Switching (SPY/TLT)', color='#1f77b4', lw=2)
    plt.plot(benchmark_value, label='Benchmark (60/40 Balanced)', color='gray', ls='--', alpha=0.6)
    
    # Dynamic Title
    plt.title(f"Pension Fund Strategy vs 60/40 Benchmark\n"
              f"Max Drawdown: Strategy {my_dd:.1%} vs Benchmark {bench_dd:.1%}", fontsize=14)
    
    plt.ylabel('Portfolio Value ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Annotation for 2008 (Ensure dates match your data range)
    if pd.Timestamp('2008-09-15') in portfolio_value.index:
        plt.annotate('2008 Crisis Protection', 
                     xy=(pd.Timestamp('2008-09-15'), portfolio_value.asof('2008-09-15')), 
                     xytext=(pd.Timestamp('2006-01-01'), portfolio_value.asof('2008-09-15') + 50000),
                     arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.show()
    
    return portfolio_value, benchmark_value

if __name__ == "__main__":
    try:
        # Load SPY and TLT
        df = load_multi_asset_data()
        
        # Run and Plot (Plotting is now handled inside the function)
        run_regime_backtest(df)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()