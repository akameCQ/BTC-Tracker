import ccxt.async_support as ccxt
import numpy as np
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
import nest_asyncio

nest_asyncio.apply()

class BtcGraphData():
    def __init__ (self, symbol='BTC/USDT', timeframe='1h'):
        self.symbol = symbol
        self.timeframe = timeframe
        self.exchange = ccxt.binance()
        
    async def get_closing_prices(self):
        try:
            ohlcv = await self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            close_prices = df['close']
            return close_prices.values
        except Exception as e:
            print(f"Error fetching data: {e}")
            return np.array([])
        finally:
            await self.exchange.close()

    def run(self):
        return asyncio.run(self.get_closing_prices())

if __name__ == "__main__":
    btc_graph_data = BtcGraphData()
    prices = btc_graph_data.run()
    print("Fetched prices:", len(prices))




