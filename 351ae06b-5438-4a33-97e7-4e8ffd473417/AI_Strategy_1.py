from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA
from surmount.logging import log

class TradingStrategy(Strategy):
    
    def __init__(self):
        # List your desired oil and green energy stocks here
        self.oil_tickers = ["OIL_STOCK_1", "OIL_STOCK_2"]
        self.green_energy_tickers = ["GREEN_ENERGY_STOCK_1", "GREEN_ENERGY_STOCK_2"]
        self.all_tickers = self.oil_tickers + self.green_energy_tickers

    @property
    def assets(self):
        return self.all_tickers

    @property
    def interval(self):
        return "1day"
    
    def sma_signal(self, ticker, data):
        """Calculates the SMA crossover signal for a given ticker and data.
        Returns True if short-term SMA is above long-term SMA, signaling upward momentum."""
        short_sma = SMA(ticker, data, length=20)  # 20-day SMA as the short-term
        long_sma = SMA(ticker, data, length=50)   # 50-day SMA as the long-term
        if short_sma is None or long_sma is None or len(short_sma) < 1 or len(long_sma) < 1:
            return False
        return short_sma[-1] > long_sma[-1]
    
    def run(self, data):
        allocation_dict = {}
        oil_signals = sum([self.sma_signal(ticker, data["ohlcv"]) for ticker in self.oil_tickers])
        green_signals = sum([self.sma_signal(ticker, data["ohlcv"]) for ticker in self.green_energy_tickers])
        
        total_signals = oil_signals + green_signals
        if total_signals == 0 or total_signals == len(self.all_tickers):
            # Equal allocation if no clear signal or both sectors are equally strong
            allocation_value = 1 / len(self.all_tickers)
            allocation_dict = {ticker: allocation_value for ticker in self.all_tickers}
        else:
            # Allocate based on momentum
            allocation_value_oil = (oil_signals / total_signals) / len(self.oil_tickers) if oil_signals > 0 else 0
            allocation_value_green = (green_signals / total_signals) / len(self.green_energy_tickers) if green_signals > 0 else 0
            for ticker in self.all_tickers:
                if ticker in self.oil_tickers:
                    allocation_dict[ticker] = allocation_value_oil
                else:  # Green energy ticker
                    allocation_dict[ticker] = allocation_value_green

        return TargetAllocation(allocation_dict)