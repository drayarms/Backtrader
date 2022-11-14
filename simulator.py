"""
Author: Ngusum Akofu
Date Created: Sept 09, 2021
"""

import sys
import strategy
import indicators 
import backtrader as bt
import plot 
import data
import pandas as pd
from pytz import timezone
import config
TimeFrame = config.TimeFrame
TimeFrameUnit = config.TimeFrameUnit 


TIMEZONE = timezone('US/Pacific')



"""
Extracts symbol as well as ohlcv for each security, packages them into a dictionary, and returns a list of dictionaries.
Parameters:
	df (pandas.DataFrame): A dataframe of daily ohlcv data for securities in play over specified time intervals.
Returns:
	ohlc ([{Float}]): A list of dictionaries. 
"""
def fill_asset_ohlc(df):
	df_indexed = df.reset_index() 
	ohlc = []

	for row in df_indexed.itertuples():	
		ohlc.append({"symbol":row.symbol, "open":row.open, "high":row.high, "low":row.low, "close":row.close})

	return ohlc



"""
Retrieves ohlc for all candlesticks within the specified start and end dates.
Parameters:
	assets (List): List of tickers of all securities in play.
	backtrader (Backtrader): Instance of backtrader class
	time_delta (String):
	time_frame (TimeFrame):
	date (pandas.Timestamp): Date for which we need previous day's daily ohlc 

Returns:
	assets_ohlc (List): List of dictionaries of each security in play's ohlcv plus ticker symbol.
	df_was_returned (Boolean): True if an actual dataframe is returned and not an empty list.
"""
def get_assets_ohlc(assets, backtrader, time_delta, time_frame, date):
	assets_ohlc = []
	df_was_returned = False

	limit = 1

	date -= pd.Timedelta(time_delta) #Go to prev day
	
	end_date = date 
	start_date = end_date - pd.Timedelta(time_delta)*limit	

	df = backtrader.get_df(config, assets, time_frame, start_date, end_date)#, False, False)
	
	if len(df) > 0:
		assets_ohlc = fill_asset_ohlc(df)
		df_was_returned = True

	return assets_ohlc, df_was_returned



"""
Retrieves ohlcv for the previous trading day's daily timeframe candlestick for each security in play. Then invokes Backtrader's run() function.
Parameters:
	start_date (pandas.Timestamp): The time specified by developer to represent the start of the simulation
	end_date (pandas.Timestamp): The time specified by developer to represent the end of the simulation
	_1min_time_delta (String):
	_1min_time_frame (TimeFrame):  
	_5min_time_delta (String): 
	_5min_time_frame (TimeFrame): 
	_15min_time_delta (String): 
	_15min_time_frame (TimeFrame): 
	day_time_delta (String): 
	day_time_frame (TimeFrame): 	

"""
def run(start_date, end_date, _1min_time_delta, _1min_time_frame, _5min_time_delta, _5min_time_frame, _15min_time_delta, _15min_time_frame, day_time_delta, day_time_frame):	

	backtrader = bt.Backtrader()
	curr_date = start_date

	assets = ['TSLA', 'XOM', 'AAPL']
	#assets = ['TSLA', 'XOM', 'AAPL', 'AAL', 'C', 'BABA', 'BAC', 'TQQQ', 'SQQQ', 'T', 'CMCSA', 'F', 'GOOG', 'PYPL']
	assets = sorted(assets)

	assets_ohlc = []
	df_was_returned = False

	assets_ohlc, df_was_returned = get_assets_ohlc(assets, backtrader, day_time_delta, day_time_frame, curr_date)

	while not df_was_returned: 
		#As long as no df was returned (meaning either holiday or weekend), continue stepping back one day and attempting to return a df
		curr_date -= pd.Timedelta(day_time_delta)	
		assets_ohlc, df_was_returned = get_assets_ohlc(assets, backtrader, day_time_delta, day_time_frame, curr_date)	

	backtrader.assets_ohlc = assets_ohlc

	stg = strategy.Strategy(len(assets), 13) #New instance of strategy used in run func
	ind = indicators.Indicators(len(assets)) #New instamce of Indicators
	plt = plot.Plot(len(assets)) #New instamce of Plot
	dt = data.Data(len(assets)) #New instance of Data

	backtrader.run(stg, assets, start_date, end_date, _1min_time_delta, _1min_time_frame, _5min_time_delta, _5min_time_frame, _15min_time_delta, _15min_time_frame, day_time_delta, day_time_frame, dt=dt, ind=ind, bt=backtrader, stg=stg, config=config, num_assets=len(assets), plt=plt, MY_TZ=TIMEZONE)



"""
The entry portal to the simulation.
"""
def main():

	MIN1_CANDLESTICK_PERIODS = {'time delta':'1 minutes', 'time frame':TimeFrame(1, TimeFrameUnit.Minute)}
	MIN5_CANDLESTICK_PERIODS = {'time delta':'5 minutes', 'time frame':TimeFrame(5, TimeFrameUnit.Minute)}
	MIN15_CANDLESTICK_PERIODS = {'time delta':'15 minutes', 'time frame':TimeFrame(15, TimeFrameUnit.Minute)}
	DAY_CANDLESTICK_PERIODS = {'time delta':'1 days', 'time frame':'1Day'}	

	_1min_time_delta = MIN1_CANDLESTICK_PERIODS.get('time delta')	
	_1min_time_frame = MIN1_CANDLESTICK_PERIODS.get('time frame')
	_5min_time_delta = MIN5_CANDLESTICK_PERIODS.get('time delta')	
	_5min_time_frame = MIN5_CANDLESTICK_PERIODS.get('time frame')
	_15min_time_delta = MIN15_CANDLESTICK_PERIODS.get('time delta')	
	_15min_time_frame = MIN15_CANDLESTICK_PERIODS.get('time frame')	
	day_time_delta = DAY_CANDLESTICK_PERIODS.get('time delta')
	day_time_frame = DAY_CANDLESTICK_PERIODS.get('time frame')		

	run(pd.Timestamp('2022-11-03 06:30',tz=TIMEZONE), pd.Timestamp('2022-11-03 13:00',tz=TIMEZONE), _1min_time_delta, _1min_time_frame, _5min_time_delta, _5min_time_frame, _15min_time_delta, _15min_time_frame, day_time_delta, day_time_frame)
	
if __name__== '__main__':
   main()
 