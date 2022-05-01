#  Main class for getting stock data
# https://towardsdatascience.com/detection-of-price-support-and-resistance-levels-in-python-baedc44c34c9
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
import yfinance
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import io
import base64

class Stocks:

    def __init__(self) -> None:
        plt.rcParams['figure.figsize'] = [12, 7]
        plt.rc('font', size=14)

        # Algorithms to idientify the 4-candle fractals
    def _is_support(self, df, i):
        return df['Low'][i] < df['Low'][i-1]  and df['Low'][i] < df['Low'][i+1] and df['Low'][i+1] < df['Low'][i+2] and df['Low'][i-1] < df['Low'][i-2]

    def _is_resistance(self, df, i):
        return df['High'][i] > df['High'][i-1]  and df['High'][i] > df['High'][i+1] and df['High'][i+1] > df['High'][i+2] and df['High'][i-1] > df['High'][i-2]

    # Function given price value l and near level s returns False if it is near some previously discovered key level
    def is_far_from_level(self, near_level, price_val, levels):
        return np.sum([abs(price_val-x) < near_level  for x in levels]) == 0

    # Translate fig -> base64 to be serviceable to html
    def _fig_to_base64(self, fig: Figure) -> bytes:
        img = io.BytesIO()
        fig.savefig(img, format='png',
                    bbox_inches='tight')
        img.seek(0)

        return base64.b64encode(img.getvalue())

    # Plots the resistance and support levels of a stock given a certain timeframe
    # Start/End must be "YYYY-MM-DD"
    def plot_by_stock(self, name: str, start: str, end: str) -> str:
        # Get the Daily Data of the ticker
        ticker = yfinance.Ticker(name)
        # TODO: Add start, end arguments
        df = ticker.history(interval='1d',start=start, end=end)

        df['Date'] = pd.to_datetime(df.index)
        df['Date'] = df['Date'].apply(mpl_dates.date2num)
        df = df.loc[:, ['Date', 'Open', 'High', 'Low', 'Close']]

        # Create a list that containts the levels we find
        levels = []
        near_level =  np.mean(df['High'] - df['Low'])
        for i in range(2,df.shape[0]-2):
            if self._is_support(df,i):
                price_val = df['Low'][i]
                if self.is_far_from_level(near_level, price_val, levels):
                    levels.append((i,price_val))
            elif self._is_resistance(df,i):
                price_val = df['High'][i]
                if self.is_far_from_level(near_level, price_val, levels):
                    levels.append((i,price_val))

        fig, ax = plt.subplots()
        candlestick_ohlc(ax,df.values,width=0.6, colorup='green', colordown='red', alpha=0.8)
        date_format = mpl_dates.DateFormatter('%d %b %Y')
        ax.xaxis.set_major_formatter(date_format)
        fig.autofmt_xdate()
        fig.tight_layout()
        for level in levels:
            plt.hlines(level[1],xmin=df['Date'][level[0]], xmax=max(df['Date']),colors='blue')
        
        # Encode the fig, return utf-8 encoded html
        encoded = self._fig_to_base64(fig)
        return '<img src="data:image/png;base64, {}">'.format(encoded.decode('utf-8'))

    
