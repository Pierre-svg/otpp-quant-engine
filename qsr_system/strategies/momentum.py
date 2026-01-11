import pandas as pd
import numpy as np
from .base import Strategy

class MovingAverageCrossover(Strategy):
    """
    A concrete implementation of the Strategy interface.
    Buys when Short MA crosses above Long MA.
    """
    def __init__(self, short_window=50, long_window=200):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        # Create a copy to avoid SettingWithCopy warnings
        signals = data.copy()
        
        # Calculate Rolling Means
        signals['short_mavg'] = data['Close'].rolling(window=self.short_window, min_periods=1).mean()
        signals['long_mavg'] = data['Close'].rolling(window=self.long_window, min_periods=1).mean()
        
        # Generate Signal (1.0 = Buy, 0.0 = Sell)
        # Using np.where is faster (vectorized) than looping
        signals['signal'] = 0.0
        signals['signal'] = np.where(signals['short_mavg'] > signals['long_mavg'], 1.0, 0.0)
        
        # Calculate 'Positions' (The change in signal)
        # 1.0 = Buy Order, -1.0 = Sell Order
        signals['positions'] = signals['signal'].diff()
        
        return signals