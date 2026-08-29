"""
Handles external market API calls
"""

import requests
import pandas as pd
import time


class MarketAPIClient:

    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"
        self.session = requests.Session()

    def fetch(self, symbol: str, interval="1d", range_period="6mo"):
        """
        Fetch historical OHLCV data.
        """

        url = f"{self.base_url}{symbol}?interval={interval}&range={range_period}"

        response = self.session.get(url)

        if response.status_code != 200:
            raise Exception("API error")

        data = response.json()

        result = data["chart"]["result"][0]
        timestamps = result["timestamp"]
        indicators = result["indicators"]["quote"][0]

        df = pd.DataFrame({
            "timestamp": timestamps,
            "open": indicators["open"],
            "high": indicators["high"],
            "low": indicators["low"],
            "close": indicators["close"],
            "volume": indicators["volume"]
        })

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df = df.dropna()

        time.sleep(0.2)  # basic rate limit

        return df

    def fetch_multiple(self, symbols: list, interval="1m", range_period="6mo"):
        """
        Fetch historical OHLCV data for multiple symbols.
        """
        all_data = {}

        for symbol in symbols:
            try:
                print(f"Fetching data for {symbol}...")
                all_data[symbol] = self.fetch(symbol, interval=interval, range_period=range_period)
            except Exception as e:
                print(f"Failed to fetch data for {symbol}: {e}")

        return all_data