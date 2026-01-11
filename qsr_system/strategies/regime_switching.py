import pandas as pd
import numpy as np
from .base import Strategy

class DualMomentum(Strategy):
    """
    Revised Strategy:
    1. If SPY > MA -> Buy SPY (Risk On)
    2. Else if TLT > MA -> Buy TLT (Safe Haven)
    3. Else -> Cash (Capital Preservation)
    """
    def __init__(self, trend_window=200):
        self.trend_window = trend_window

    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Returns a DataFrame with weights:
        - 'SPY': 1.0, 0.0, or 0.0
        - 'TLT': 0.0, 1.0, or 0.0
        - (Implicitly Cash if both are 0)
        """
        signals = pd.DataFrame(index=market_data.index)
        
        # 1. Calculate Trends for BOTH assets
        spy_price = market_data['SPY']
        tlt_price = market_data['TLT']
        
        spy_ma = spy_price.rolling(window=self.trend_window).mean()
        tlt_ma = tlt_price.rolling(window=self.trend_window).mean()
        
        # 2. Define Logic (0 = Cash, 1 = SPY, 2 = TLT)
        # We use a helper column 'choice' to make logic readable
        choice = pd.Series(0, index=signals.index) # Default to 0 (Cash)
        
        # Condition: SPY is bullish
        choice[spy_price > spy_ma] = 1 
        
        # Condition: SPY is bearish BUT TLT is bullish
        # Note: We only buy TLT if SPY is down AND TLT is actually going up
        condition_tlt = (spy_price <= spy_ma) & (tlt_price > tlt_ma)
        choice[condition_tlt] = 2
        
        # 3. Create Weights based on choice
        signals['spy_weight'] = np.where(choice == 1, 1.0, 0.0)
        signals['tlt_weight'] = np.where(choice == 2, 1.0, 0.0)
        # If choice is 0, both weights are 0.0 -> We hold Cash.
        
        return signals