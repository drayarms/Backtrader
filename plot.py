"""
Author: Ngusum Akofu
Date Created: Feb 24, 2021
"""

import matplotlib.pyplot as mplt
from mpl_finance import candlestick_ohlc
#import matplotlib.dates as mdates
import matplotlib.ticker as mticker	



class Plot:
	


	def __init__(self, num_assets):

		self.ax = mplt.gca()
		self.ax1 = mplt.subplot2grid((1,1), (0,0))	
		self.fig = mplt.figure()
		self.ax3D = self.fig.add_subplot(111, projection='3d')

		self.time_list = []
		self.price_list = []
		self.ema12_list = []
		self.ohlc = []

		for i in range(0, num_assets):
			self.time_list.append([[],[],[]])
			self.price_list.append([[],[],[]])
			self.ema12_list.append([[],[],[]])
			self.ohlc.append([[],[],[]])		



	"""
	Stores ohlcv data as well as any indicators developer may wish to include, for all securities in play for a given timeframe, at the current minute.
	Parameters:
		assets ([String]): A list of the securities in play sorted alphabetically by ticker symbol.
		time (pandas.TimeFrame): Current minute.
		price ([Float]): List of close prices for all securities in play, for the specified timeframe and the current minute
		ema12 ([Float]): List of ema12 for all securities in play, for the specified timeframe and the current minute
		candlestick ([(Float, Float, Float, Float, Float, Float)]): ohlcv for all securities in play for specified timeframe and current minute. 
	"""
	def populate_axes(self, assets, time, price, ema12, candlestick, timeframe_index):
		for i in range(0, len(assets)):
			self.time_list[i][timeframe_index].append(time.timestamp())#Each entry is a time obj
			self.price_list[i][timeframe_index].append(price[i])#Each entry is a list of the closing price of each stock		
			self.ema12_list[i][timeframe_index].append(ema12[i])#Each entry is a list of the ema12 of each stock
			self.ohlc[i][timeframe_index].append(candlestick[i])
	


	"""
	Plots candlesticks and indicators.
	Parameters:
		strategy (Strategy): Instance of Strategy class.
		ticker (String): Symbol of the security under consideration
		i (Int): Indexed position of the security under consideration in assets list.
		kwargs
	"""
	def plot_full_chart(self, ticker, i, kwargs):
		ax1 = mplt.subplot2grid((1,1), (0,0))	
		candlestick_ohlc(ax1, self.ohlc[i][1], width=40, colorup='green', colordown='red')
		ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
		ax1.grid(True)

		mplt.xlabel('Date')
		mplt.ylabel('Price')
		mplt.title(ticker)
		mplt.subplots_adjust(left=0.09, bottom=0.02, right=0.94, top=0.90, wspace=0.4, hspace=0)
		ax1.plot(self.time_list[i][1], self.ema12_list[i][1])
	
		mplt.show()	

