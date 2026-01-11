import numpy as np
import pandas as pd

def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    """
    Calculates the Annualized Sharpe Ratio.
    Sharpe = (Mean Return - Risk Free) / Volatility
    """
    if returns.std() == 0:
        return 0.0
    
    # We assume daily data (252 trading days)
    excess_return = returns - (risk_free_rate / 252)
    annualized_return = excess_return.mean() * 252
    annualized_vol = excess_return.std() * np.sqrt(252)
    
    return annualized_return / annualized_vol

def calculate_max_drawdown(equity_curve):
    """
    Calculates the Maximum Drawdown (Worst peak-to-valley drop).
    Input: Series of Portfolio Value (Dollar amount)
    """
    # Calculate rolling maximum (The "Peak" so far)
    running_max = equity_curve.cummax()
    
    # Calculate drawdown percentage
    drawdown = (equity_curve - running_max) / running_max
    
    # Return the minimum (most negative) value
    return drawdown.min()