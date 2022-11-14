"""
Author: Ngusum Akofu
Date Created: Sept 09, 2021
Mod Sept 07 aft
"""

import numpy as np
import pandas as pd

class Strategy:


	
	def __init__(self, num_assets, rows_limit):

		self._1min_time_intervals = [] 
		self._1min_close_prices = [] 
		self._1min_open_prices = []
		self._1min_hi_prices = [] 
		self._1min_lo_prices = [] 
		self._1min_vols = [] 

		self._5min_time_intervals = [] 
		self._5min_close_prices = [] 
		self._5min_open_prices = []
		self._5min_hi_prices = [] 
		self._5min_lo_prices = [] 
		self._5min_vols = [] 

		self._15min_time_intervals = [] 
		self._15min_close_prices = [] 
		self._15min_open_prices = []
		self._15min_hi_prices = [] 
		self._15min_lo_prices = [] 
		self._15min_vols = [] 	

		self.rows_limit = rows_limit#10#201#51#16

		self._1min_growing_candlestick = []
		self._5min_growing_candlestick = []
		self._15min_growing_candlestick = []

		for i in range(0, num_assets):
			self._5min_growing_candlestick.append({"open":-1, "close":-1, "lo":-np.inf, "hi":np.inf, "vol":-1})	
			self._15min_growing_candlestick.append({"open":-1, "close":-1, "lo":-np.inf, "hi":np.inf, "vol":-1})	




	"""
	Checks if the two timestamps supplied are from the same day.
	Parameters:
		date1 (pandas.Timestamp):
		date2 (pandas.Timestamp):
	Returns:
		(Boolean): True if the two timestamps supplied as arguments are from the same day. 
	"""
	def is_same_day(self, date1, date2):
		return date1.year == date2.year and date1.month == date2.month and date1.day == date2.day



	"""
	Determines whether or not it is the last minute prior to the end of the trading day before the closing bell.
	Parameters:
		curr_date (pandas.Timestamp): The timestamp under consideration.
		start_trading_day (pandas.Timestamp): The timestamp representing the open of the trading day.
		end_trading_day (pandas.Timestamp): The timestamp representing the end of the trading day.
	Returns:
		(Boolean): True if it is the last minute prior to the end of the trading day.
	"""
	def is_day_close(self, curr_date, start_trading_day, end_trading_day):
		return self.is_same_day(curr_date, start_trading_day) and  curr_date == end_trading_day - pd.Timedelta('1minutes') 



	"""
	Determines which point prior to the start of the trading day, developer desires to start plotting candlesticks.
	Parameters:
		curr_date (pandas.Timestamp): The timestamp under consideration.
		start_trading_day (pandas.Timestamp): The timestamp representing the open of the trading day.
	Returns:
		(Boolean): True if current timestamp is to the right on the timeline, of the timestamp which developer picked to start plotting candlesticks.		
	"""
	def plot_curr_date(self, curr_date, start_trading_day):
		return curr_date.timestamp() >= (start_trading_day - pd.Timedelta('0 minutes')).timestamp() 



	"""
	For timeframes exceeding 1 minute, the ohlc values change by the minute. We attempt to simulate these changes from the moment when a new candlestick
	for the given timeframe first appears on the chart, to the time when it has fully formed.
	Parameters:
		assets ([String]): A list of the securities in play sorted alphabetically by ticker symbol.
		timeframe (Timeframe): 1, 5, or 15 min
		growing_candlestick ([{Float}]): A list containing dictionaries, each of which contaiins ohlcv data for each security in play.
		curr_date (pandas.Timestamp): The timestamp under consideration.
		_1min_close_price ([Float]): A list of close prices for current 1 minute candlesticks, of all securities in play, sorted alphabetically by ticker symbols.
		_1min_open_price ([Float]): A list of open prices for current 1 minute candlesticks, of all securities in play, sorted alphabetically by ticker symbols.
		_1min_hi_price ([Float]): A list of high prices for current 1 minute candlesticks, of all securities in play, sorted alphabetically by ticker symbols.
		_1min_lo_price ([Float]): A list of low prices for current 1 minute candlesticks, of all securities in play, sorted alphabetically by ticker symbols.
		_1min_vol ([Float]): A list of volumes for current 1 minute candlesticks, of all securities in play, sorted alphabetically by ticker symbols.
	Returns:	

		timestamps ([pandas.Timestamp]): A list of of the current minute's timestamp.
		close_prices ([[float]]): A list of a list of the close prices of all the securities in play as of the current minute.
		open_prices ([[float]]): A list of a list of the open prices of all the securities in play as of the current minute.
		hi_prices ([[float]]): A list of a list of the high prices of all the securities in play as of the current minute.
		lo_prices ([[float]]): A list of a list of the low prices of all the securities in play as of the current minute.
		vols ([[float]]): A list of a list of the volumes of all the securities in play as of the current minute.
		growing_candlestick ([{float}]): A list of dictionaries, each of which holds ohlcv data for each security in play as of the current minute. Represents the current dynamic candlestick.
	"""
	def get_growing_candlestick(self, assets, timeframe, growing_candlestick, curr_date, _1min_close_price, _1min_open_price, _1min_hi_price, _1min_lo_price, _1min_vol):
		
		timestamps = [curr_date]
		close_prices = [[]]
		open_prices = [[]]
		hi_prices = [[]]
		lo_prices = [[]]
		vols = [[]]

		for i in range(0, len(assets)):
			curr_close = _1min_close_price[i]
			curr_open = _1min_open_price[i]
			curr_hi = _1min_hi_price[i]
			curr_lo = _1min_lo_price[i]
			curr_vol = _1min_vol[i]

			prev_close = growing_candlestick[i].get("close")
			prev_open = growing_candlestick[i].get("open")
			prev_hi = growing_candlestick[i].get("hi")
			prev_lo = growing_candlestick[i].get("lo")
			prev_vol = growing_candlestick[i].get("vol")

			close = 0
			opn = 0
			hi = 0
			lo = 0
			vol = 0
			if curr_date.minute % timeframe == 1: #First minute of fresh candlestick
				close  = curr_close
				opn = curr_open
				hi = curr_hi
				lo = curr_lo
				vol = curr_vol
			else:#Growing candlestick
				close  = curr_close #Close should be most recent close
				opn = prev_open #Open should remain same as first minute open
				hi = max(curr_hi, prev_hi)
				lo = min(curr_lo, prev_lo)
				vol = curr_vol+prev_vol

			growing_candlestick[i].update({"close":close})
			growing_candlestick[i].update({"open":opn})
			growing_candlestick[i].update({"hi":hi})
			growing_candlestick[i].update({"lo":lo})
			growing_candlestick[i].update({"vol":vol})	
			close_prices[0].append(close)
			open_prices[0].append(opn)	
			hi_prices[0].append(hi)
			lo_prices[0].append(lo)
			vols[0].append(vol)

		return timestamps, close_prices, open_prices, hi_prices, lo_prices, vols, growing_candlestick 



	"""
	Determines the ohlcv for each security in play as of the current minute, and places them in data files. These values will be later retrieved to create ohlcv lists for each security in play, for the last n candlesticks.
	Parameters:
		backtrader (Backtrader): Instance of backtrader class. 
		assets ([String]): A list of the securities in play sorted alphabetically by ticker symbol.
		time_delta (String):
		time_frame (Timeframe):
		time_frame_number (Int): 
		curr_date (pandas.Timestamp): Current minute.
		_1min_close_price ([Float]): A list of close prices for current 1 minute candlesticks, of all securities in play, sorted alphabetically by ticker symbols.
		_1min_open_price ([Float]): A list of open prices for current 1 minute candlesticks, of all securities in play, sorted alphabetically by ticker symbols.
		_1min_hi_price ([Float]): A list of high prices for current 1 minute candlesticks, of all securities in play, sorted alphabetically by ticker symbols.
		_1min_lo_price ([Float]): A list of low prices for current 1 minute candlesticks, of all securities in play, sorted alphabetically by ticker symbols.
		_1min_vol ([Float]): A list of volumes for current 1 minute candlesticks, of all securities in play, sorted alphabetically by ticker symbols.		
		open_file (String): File to which the open prices for all securities in play as of the current minute, will be written to.
		high_file (String): File to which the high prices for all securities in play as of the current minute, will be written to.
		low_file (String): File to which the low prices for all securities in play as of the current minute, will be written to.
		close_file (String): File to which the close prices for all securities in play as of the current minute, will be written to.
		vol_file (String): File to which the volume prices for all securities in play as of the current minute, will be written to.
		growing_candlestick ([{float}]): A list of dictionaries, each of which holds ohlcv data for each security in play as of the current minute. Represents the current dynamic candlestick.
		this_time_intervals ([pandas.Timestamp]): A list of of the current minute's timestamp.
		_this_close_prices ([Float]): A list of close prices for current 1 minute candlesticks, of all securities in play, sorted alphabetically by ticker symbols.
		_this_open_prices ([Float]): A list of open prices for current 1 minute candlesticks, of all securities in play, sorted alphabetically by ticker symbols.
		_this_hi_prices ([Float]): A list of high prices for current 1 minute candlesticks, of all securities in play, sorted alphabetically by ticker symbols.
		_this_lo_prices ([Float]): A list of low prices for current 1 minute candlesticks, of all securities in play, sorted alphabetically by ticker symbols.
		_this_vols ([Float]): A list of volumes for current 1 minute candlesticks, of all securities in play, sorted alphabetically by ticker symbols.
		interval (Int): 5 or 15 minute interval
		kwargs	
	"""
	def add_rows_to_files(self, backtrader, assets, time_delta, time_frame, curr_date, _1min_close_price, _1min_open_price, _1min_hi_price, _1min_lo_price, _1min_vol, open_file, high_file, low_file, close_file, vol_file, growing_candlestick, this_time_intervals, this_close_prices, this_open_prices, this_hi_prices, this_lo_prices, this_vols, interval, kwargs):
		time_intervals, close_prices, open_prices, hi_prices, lo_prices, vols, vwaps = [], [], [], [], [], [] ,[]
		if curr_date.minute % interval == 0:#Get last bar which will be mature. New bar not yet available till next min
			time_intervals, close_prices, open_prices, hi_prices, lo_prices, vols, vwaps = backtrader.get_closes_opens_his_los_vols_vwaps(kwargs['config'], assets, time_delta, time_frame, 1, (curr_date - pd.Timedelta(time_delta)))#, False, False)
		else:
			time_intervals, close_prices, open_prices, hi_prices, lo_prices, vols, growing_candlestick = self.get_growing_candlestick(assets, interval, growing_candlestick, curr_date, _1min_close_price, _1min_open_price, _1min_hi_price, _1min_lo_price, _1min_vol)
			#Note: time_intervals returned above is local not UTC unlike from raw df
		
		if curr_date.minute % interval == 1:#Fresh 5 min candlestick starts
			kwargs['dt'].add_row_to_data_files(time_intervals, open_prices, hi_prices, lo_prices, close_prices, vols, open_file, high_file, low_file, close_file, vol_file)
		else:
			#Replace last row. Delete it then add new one.
			kwargs['dt'].delete_last_row_from_data_files(open_file, high_file, low_file, close_file, vol_file)
			kwargs['dt'].add_row_to_data_files(time_intervals, open_prices, hi_prices, lo_prices, close_prices, vols, open_file, high_file, low_file, close_file, vol_file)				




	"""
	Generates ohlcv for each security in play for various timeframes (in this case, 1min, 5min, 15min), as often as the developer needs to (in this case, once a minute)
	This data can then be used to compute most indicators needed for implementing the strategy.
	Parameters:
		backtrader (Backtrader): Instance of backtrader class. 
		assets ([String]): A list of the securities in play sorted alphabetically by ticker symbol.
		curr_date (Timestamp): Current minute.
		start_execution_time (pandas.Timestamp): Minute when developer desires algorithm to begin execution.
		start_trading_day (pandas.Timestamp): Minute when the trading day starts.
		end_trading_day (pandas.Timestamp): Minute when the trading day ends.
		_1min_time_delta (String):
		_1min_time_frame (TimeFrame):  
		_5min_time_delta (String): 
		_5min_time_frame (TimeFrame): 
		_15min_time_delta (String): 
		_15min_time_frame (TimeFrame): 
		day_time_delta (String): 
		day_time_frame (TimeFrame): 
		kwargs	
	"""
	#FUNCTION MUST BE IMPLEMENTED BY USER
	def execute(self, backtrader, assets, curr_date, start_execution_time, start_trading_day, end_trading_day, _1min_time_delta, _1min_time_frame, _5min_time_delta, _5min_time_frame, _15min_time_delta, _15min_time_frame, day_time_delta, day_time_frame, kwargs):
	
		print("date "+str(curr_date))
		if curr_date.minute % 5 == 0 and curr_date.minute % 15 != 0:
			print("************************\n")
		if curr_date.minute % 15 == 0:
			print("++++++++++++++++++++++++++++++\n\n")

		limit = self.rows_limit



		#1MIN TIMEFRAME
		_1min_time_intervals, _1min_close_prices, _1min_open_prices, _1min_hi_prices, _1min_lo_prices, _1min_vols, _1min_vwaps = backtrader.get_closes_opens_his_los_vols_vwaps(kwargs['config'], assets, _1min_time_delta, _1min_time_frame, 1, (curr_date - pd.Timedelta(_1min_time_delta)))#, False, False)
			
		kwargs['dt'].add_row_to_data_files(_1min_time_intervals, _1min_open_prices, _1min_hi_prices, _1min_lo_prices, _1min_close_prices, _1min_vols, 'data_files/_1min_open.cvs', 'data_files/_1min_high.cvs', 'data_files/_1min_low.cvs', 'data_files/_1min_close.cvs', 'data_files/_1min_volume.cvs')

		_1min_time_intervals_read_from_file, _1min_open_prices_read_from_file, _1min_hi_prices_read_from_file, _1min_lo_prices_read_from_file, _1min_close_prices_read_from_file, _1min_vols_read_from_file = kwargs['dt'].get_rows_from_files('data_files/_1min_open.cvs', 'data_files/_1min_high.cvs', 'data_files/_1min_low.cvs', 'data_files/_1min_close.cvs', 'data_files/_1min_volume.cvs', self._5min_time_intervals, self._5min_close_prices, self._5min_open_prices, self._5min_hi_prices, self._5min_lo_prices, self._5min_vols, limit)

		_1min_close_price = _1min_close_prices_read_from_file[-1] 
		_1min_open_price = _1min_open_prices_read_from_file[-1]
		_1min_hi_price = _1min_hi_prices_read_from_file[-1] 
		_1min_lo_price = _1min_lo_prices_read_from_file[-1]
		_1min_vol = _1min_vols_read_from_file[-1] 

		_1min_candlestick_ohlc_all_stocks = []

		#Generate indicators
		kwargs['ind']._1min_ema12 = kwargs['ind'].generate_indicators(_1min_close_prices_read_from_file, kwargs['ind']._1min_ema12)

		for i in range(0, len(assets)):
			_1min_candlestick_ohlc = curr_date.timestamp(), _1min_open_price[i], _1min_hi_price[i], _1min_lo_price[i], _1min_close_price[i], _1min_vol[i]
			_1min_candlestick_ohlc_all_stocks.append(_1min_candlestick_ohlc)

		if self.plot_curr_date(curr_date, start_trading_day):
			kwargs['plt'].populate_axes(assets, curr_date, _1min_close_price, kwargs['ind']._1min_ema12, _1min_candlestick_ohlc_all_stocks, 0)					

	

		#5MIN TIMEFRAME 
		self.add_rows_to_files(backtrader, assets, _5min_time_delta, _5min_time_frame, curr_date, _1min_close_price, _1min_open_price, _1min_hi_price, _1min_lo_price, _1min_vol, 'data_files/_5min_open.cvs', 'data_files/_5min_high.cvs', 'data_files/_5min_low.cvs', 'data_files/_5min_close.cvs', 'data_files/_5min_volume.cvs', self._5min_growing_candlestick, self._5min_time_intervals, self._5min_close_prices, self._5min_open_prices, self._5min_hi_prices, self._5min_lo_prices, self._5min_vols, 5, kwargs)
		_5min_time_intervals, _5min_open_prices_read_from_file, _5min_hi_prices_read_from_file, _5min_lo_prices_read_from_file, _5min_close_prices_read_from_file, _5min_vols_read_from_file = kwargs['dt'].get_rows_from_files('data_files/_5min_open.cvs', 'data_files/_5min_high.cvs', 'data_files/_5min_low.cvs', 'data_files/_5min_close.cvs', 'data_files/_5min_volume.cvs', self._5min_time_intervals, self._5min_close_prices, self._5min_open_prices, self._5min_hi_prices, self._5min_lo_prices, self._5min_vols, limit)
		_5min_close_price = _5min_close_prices_read_from_file[-1] 
		_5min_open_price = _5min_open_prices_read_from_file[-1]
		_5min_hi_price = _5min_hi_prices_read_from_file[-1] 
		_5min_lo_price = _5min_lo_prices_read_from_file[-1]
		_5min_vol = _5min_vols_read_from_file[-1] 			

		if curr_date.minute % 5 == 4:
			_5min_candlestick_ohlc_all_stocks = []
			
			#Generate indicators
			kwargs['ind']._5min_ema12 = kwargs['ind'].generate_indicators(_5min_close_prices_read_from_file, kwargs['ind']._5min_ema12)

			for i in range(0, len(assets)):
				_5min_candlestick_ohlc = curr_date.timestamp(), _5min_open_price[i], _5min_hi_price[i], _5min_lo_price[i], _5min_close_price[i], _5min_vol[i]
				_5min_candlestick_ohlc_all_stocks.append(_5min_candlestick_ohlc)

			if self.plot_curr_date(curr_date, start_trading_day):
				kwargs['plt'].populate_axes(assets, curr_date, _5min_close_price, kwargs['ind']._5min_ema12, _5min_candlestick_ohlc_all_stocks, 1)
				


		#15MIN TIMEFRAME
		self.add_rows_to_files(backtrader, assets, _15min_time_delta, _15min_time_frame, curr_date, _1min_close_price, _1min_open_price, _1min_hi_price, _1min_lo_price, _1min_vol, 'data_files/_15min_open.cvs', 'data_files/_15min_high.cvs', 'data_files/_15min_low.cvs', 'data_files/_15min_close.cvs', 'data_files/_15min_volume.cvs', self._15min_growing_candlestick, self._15min_time_intervals, self._15min_close_prices, self._15min_open_prices, self._15min_hi_prices, self._15min_lo_prices, self._15min_vols, 15, kwargs)
		_15min_time_intervals, _15min_open_prices_read_from_file, _15min_hi_prices_read_from_file, _15min_lo_prices_read_from_file, _15min_close_prices_read_from_file, _15min_vols_read_from_file = kwargs['dt'].get_rows_from_files('data_files/_15min_open.cvs', 'data_files/_15min_high.cvs', 'data_files/_15min_low.cvs', 'data_files/_15min_close.cvs', 'data_files/_15min_volume.cvs', self._15min_time_intervals, self._15min_close_prices, self._15min_open_prices, self._15min_hi_prices, self._15min_lo_prices, self._15min_vols, limit)
		_15min_close_price = _15min_close_prices_read_from_file[-1] 
		_15min_open_price = _15min_open_prices_read_from_file[-1]
		_15min_hi_price = _15min_hi_prices_read_from_file[-1] 
		_15min_lo_price = _15min_lo_prices_read_from_file[-1]
		_15min_vol = _15min_vols_read_from_file[-1] 

		if curr_date.minute % 15 == 14:
			_15min_candlestick_ohlc_all_stocks = []

			#Generate indicators
			kwargs['ind']._15min_ema12 = kwargs['ind'].generate_indicators(_15min_close_prices_read_from_file, kwargs['ind']._15min_ema12)

			for i in range(0, len(assets)):
				_15min_candlestick_ohlc = curr_date.timestamp(), _15min_open_price[i], _15min_hi_price[i], _15min_lo_price[i], _15min_close_price[i], _15min_vol[i]
				_15min_candlestick_ohlc_all_stocks.append(_15min_candlestick_ohlc)	

			if self.plot_curr_date(curr_date, start_trading_day):
				kwargs['plt'].populate_axes(assets, curr_date, _15min_close_price, kwargs['ind']._15min_ema12, _15min_candlestick_ohlc_all_stocks, 2)







		#IIMPLEMENT YOUR STRATEGY HERE

		





		if self.is_same_day(curr_date, start_trading_day) and curr_date.timestamp() >= start_trading_day.timestamp():	
			if self.is_day_close(curr_date, start_trading_day, end_trading_day):
				for i in range(0, len(assets)):
					kwargs['plt'].plot_full_chart(assets[i], i, kwargs)
					#kwargs['plt'].plot_full_chart(self, start_trading_day, assets[i], i, kwargs)





		

