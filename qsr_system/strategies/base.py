from abc import ABC, abstractmethod
import pandas as pd

class Strategy(ABC):
    """
    Abstract Base Class (Interface) for all trading strategies.
    
    Why use this? 
    It enforces a contract: Every new strategy we build MUST have 
    a 'generate_signals' method. This prevents bugs in the future.
    """
    
    @abstractmethod
    def generate_signals(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Input: A DataFrame of market data (Close, Volume, etc.)
        Output: A DataFrame with a 'Signal' column (1 for Buy, -1 for Sell, 0 for Hold)
        """
        pass