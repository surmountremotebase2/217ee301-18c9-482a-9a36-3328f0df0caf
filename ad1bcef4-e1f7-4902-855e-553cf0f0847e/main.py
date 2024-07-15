from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, SMA
from surmount.data import InsiderTrading, SocialSentiment
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Hypothetical tickers related to wellness, sports, and wellbeing
        self.tickers = ["NKE", "LULU", "PLNT", "GILD"]
        self.data_list = []
        for ticker in self.tickers:
            self.data_list.append(InsiderTrading(ticker))
            self.data_list.append(SocialSentiment(ticker))

    @property
    def interval(self):
        # Choosing a daily interval for analysis
        return "1day"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            # Initialize allocation
            allocation_dict[ticker] = 0.0
            
            # Sentiment analysis - more emphasis on social sentiment
            if ("social_sentiment", ticker) in data:
                sentiment_data = data[("social_sentiment", ticker)]
                if sentiment_data and len(sentiment_data) > 0:
                    recent_sentiment = sentiment_data[-1]['twitterSentiment'] + sentiment_data[-1]['stocktwitsSentiment']
                    # If sentiment is positive, consider allocating
                    if recent_sentiment > 1.0:  # Arbitrary threshold for 'positive' sentiment
                        allocation_dict[ticker] += 0.2
            
            # Insider Trading analysis - cautious about recent sell-offs
            if ("insider_trading", ticker) in data:
                insiders = data[("insider_trading", ticker)]
                if insiders and len(insiders) > 0:
                    latest_insider_activity = insiders[-1]['transactionType']
                    # If the latest activity is a sale, reduce investment or avoid increasing it
                    if "Sale" in latest_insider_activity:
                        allocation_dict[ticker] -= 0.1  # Reduce allocation if recent insider selling
            
            # Normalize allocations if any are negative after adjustments
            if allocation_dict[ticker] < 0:
                allocation_dict[ticker] = 0.0
        
        # Normalize allocations to ensure they sum to 1
        total_allocation = sum(allocation_dict.values())
        if total_allocation > 0:
            for ticker in allocation_dict:
                allocation_dict[ticker] /= total_allocation
        
        return TargetAllocation(allocation_dict)