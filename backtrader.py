"""
Author: Ngusum Akofu
Date Created: Nov 18, 2020
"""
import pandas as pd
from urllib.error import HTTPError
from werkzeug.exceptions import HTTPException
import time


class Backtrader:



	def __init__(self):
		self.assets_ohlc = []



	"""
	Returns a pandas dataframe for securities specified within the time range specified by start date and end date, at intervals specified by the timeframe
	Parameters:
		config: Reference to config.py
		assets ([String]): A list of the securities in play sorted alphabetically by ticker symbol.
		time_frame (TimeFrame):
		start_dt (pandas.Timestamp): Specifies the begining of the time range for which the dataframe is requested. 
		end_dt (pandas.Timestamp): Specifies the end of the time range for which the dataframe is requested. 

	Returns:
		barset.df (pandas.DataFrame): Dataframe for securities specified within the time range specified by start date and end date, at intervals specified by the timeframe
	"""
	def _get_df(self, config, assets, time_frame, start_dt, end_dt):
		def get_barset(assets):

			barset_got = False
			while(not barset_got):
				try:
					return config.api.get_bars(assets, time_frame, start_dt, end_dt, adjustment='raw')

				#except HTTPError:
				except HTTPException:
					print("Waiting before retrying...")
					time.sleep(3)#Suspends thread for specified num seconds					
					barset_got = False

		barset = get_barset(assets)

		return barset.df



	"""
	Transforms a dataframe into a one dimensional list.
	Parameters:
		flattened_df (pandas.DataFrame): A single column dataframe.
		num_assets (Int): Number of securities in play
		limit (Int): Number of candlsticks represented in dataframe.
	Returns:
		arr ([[Float]]): List containing the values extracted from non-indexed column of the dataframe
	"""
	def unflatten(self, flattened_df, num_assets, limit):#, num_rows):
		arr = []
		for i in range(0, limit):
			row = [] #Each row is a time df
			for j in range(0, num_assets):
				row.append(flattened_df[(limit*j) + i])
			arr.append(row)
		return arr



	"""
	Returns a pandas dataframe for securities specified within the time range specified by start date and end date, at intervals specified by the timeframe
	Parameters:
		config: Reference to config.py
		assets ([String]): A list of the securities in play sorted alphabetically by ticker symbol.
		time_frame (TimeFrame):
		start_dt (pandas.Timestamp): Specifies the begining of the time range for which the dataframe is requested. 
		end_dt (pandas.Timestamp): Specifies the end of the time range for which the dataframe is requested. 

	Returns:
		(pandas.DataFrame): Dataframe for securities specified within the time range specified by start date and end date, at intervals specified by the timeframe
	"""
	def get_df(self, config, assets, time_frame, start_dt, end_dt):
		return self._get_df(config, assets, time_frame, start_dt.isoformat(), end_dt.isoformat())




	"""
	Ensures that all rows of the same security appear contiguously in a single block. In the raw dataframe, some rows may ocassinaly be out of place.
	Parameters:
		df (pandas.DataFrame): The raw dataframe which may have some rows out of place (ie not contiguous with all the other rows of the same security).
		assets ([String]): A list of the securities in play sorted alphabetically by ticker symbol.

	Returns:
		df (pandas.DataFrame): Rearrange dataframe (all rows of the same security appear contiguously).
	"""
	def rearrange_rows_by_symbol(self, df, assets):

		def fill_lists(timestamps, timestamp, opens, opn, highs, high, lows, low, closes, close, volumes, volume, trade_counts, trade_count, vwaps, vwap, symbols, symbol):
			timestamps.append(timestamp)
			opens.append(opn)
			highs.append(high)
			lows.append(low)
			closes.append(close)
			volumes.append(volume)
			trade_counts.append(trade_count)
			vwaps.append(vwap)
			symbols.append(symbol)			
		df_indexed = df.reset_index()  #Mmake sure indexes pair with number of rows
	
		timestamps = []
		opens = []
		highs = []
		lows= []
		closes = []
		volumes = []
		trade_counts = []
		vwaps = []
		symbols = []

		for i in range(0, len(assets)):

			for row in df_indexed.itertuples():
				if assets[i] == row.symbol:
					#Insert row
					fill_lists(timestamps, row.timestamp, opens, row.open, highs, row.high, lows, row.low, closes, row.close, volumes, row.volume, trade_counts, row.trade_count, vwaps, row.vwap, symbols, row.symbol)				

		df = pd.DataFrame({
    		'open': opens,
    		'high': highs,
    		'low': lows,
    		'close': closes,
    		'volume':volumes,
    		'trade_count':trade_counts,
    		'vwap':vwaps,
    		'symbol':symbols

		},index=timestamps)	
		df.index.name = 'timestamp'		

		return df



	"""
	Some securities particularly during pre and post market hours, may be missing some candlesticks. This function interpolates the dataframe to fill those missing candlesticks.
	Parameters:
		df (pandas.DataFrame): The raw dataframe which may be missing some candlesticks for some securities.
		time_delta (String):
		start_date (pandas.Timestamp): Specifies the begining of the time range. 
		end_date (pandas.Timestamp): Specifies the end of the time range. 
	Returns:
		df (pandas.DataFrame): A copy of the raw dataframe with missing candlesticks filled in. 
	"""
	def fill_missing_dates(self, df, time_delta, start_date, end_date):

		def fill_lists(timestamps, timestamp, opens, opn, highs, high, lows, low, closes, close, volumes, volume, trade_counts, trade_count, vwaps, vwap, symbols, symbol):
			timestamps.append(timestamp)
			opens.append(opn)
			highs.append(high)
			lows.append(low)
			closes.append(close)
			volumes.append(volume)
			trade_counts.append(trade_count)
			vwaps.append(vwap)
			symbols.append(symbol)			
		
		#Dataframe returns dates in UTC. So need to convert from local time to UTC
		dataframe_start_dt_utc = start_date.tz_convert('UTC')
		dataframe_end_dt_utc = end_date.tz_convert('UTC')
		dataframe_end_dt_utc_hour_min = dataframe_end_dt_utc.replace(second=0, microsecond=0)	

		df_indexed = df.reset_index()  # make sure indexes pair with number of rows
		prev_row = None

		timestamps = []
		opens = []
		highs = []
		lows= []
		closes = []
		volumes = []
		trade_counts = []
		vwaps = []
		symbols = []
		num_symbols = 1

		for row in df_indexed.itertuples():
			if row.Index > 0:

				if prev_row.symbol == row.symbol:
					expected_time = prev_row.timestamp + pd.Timedelta(time_delta)
					expected_time_hour_min = expected_time.replace(second=0, microsecond=0)
					row_timestamp_hour_min = row.timestamp.replace(second=0, microsecond=0)
					while expected_time_hour_min < row_timestamp_hour_min:					
						#Expected time was skipped. Insert before current row.
						fill_lists(timestamps, expected_time, opens, row.open, highs, row.high, lows, row.low, closes, row.close, volumes, row.volume, trade_counts, row.trade_count, vwaps, row.vwap, symbols, row.symbol)
						expected_time += pd.Timedelta(time_delta)
						expected_time_hour_min = expected_time.replace(second=0, microsecond=0)

					fill_lists(timestamps, row.timestamp, opens, row.open, highs, row.high, lows, row.low, closes, row.close, volumes, row.volume, trade_counts, row.trade_count, vwaps, row.vwap, symbols, row.symbol)	

				
				else:#End of an old symbol and start of a new symbol
					num_symbols += 1
					#End of old symbol
					last_time_slot = prev_row.timestamp
					last_time_slot_hour_min = last_time_slot.replace(second=0, microsecond=0)
					if last_time_slot_hour_min < dataframe_end_dt_utc_hour_min:
						last_time_slot += pd.Timedelta(time_delta)
						last_time_slot_hour_min = last_time_slot.replace(second=0, microsecond=0)
						fill_lists(timestamps, last_time_slot, opens, prev_row.open, highs, prev_row.high, lows, prev_row.low, closes, prev_row.close, volumes, prev_row.volume, trade_counts, prev_row.trade_count, vwaps, prev_row.vwap, symbols, prev_row.symbol)	
					while last_time_slot_hour_min < dataframe_end_dt_utc_hour_min:
						last_time_slot += pd.Timedelta(time_delta)
						last_time_slot_hour_min = last_time_slot.replace(second=0, microsecond=0)
						fill_lists(timestamps, last_time_slot, opens, prev_row.open, highs, prev_row.high, lows, prev_row.low, closes, prev_row.close, volumes, prev_row.volume, trade_counts, prev_row.trade_count, vwaps, prev_row.vwap, symbols, prev_row.symbol)	
					
					#Start of new symbol
					expected_time = dataframe_start_dt_utc
					expected_time_hour_min = expected_time.replace(second=0, microsecond=0)
					row_timestamp_hour_min = row.timestamp.replace(second=0, microsecond=0)
					while expected_time_hour_min < row_timestamp_hour_min:
						fill_lists(timestamps, expected_time, opens, row.open, highs, row.high, lows, row.low, closes, row.close, volumes, row.volume, trade_counts, row.trade_count, vwaps, row.vwap, symbols, row.symbol)
						expected_time += pd.Timedelta(time_delta)	
						expected_time_hour_min = expected_time.replace(second=0, microsecond=0)					
					
					fill_lists(timestamps, row.timestamp, opens, row.open, highs, row.high, lows, row.low, closes, row.close, volumes, row.volume, trade_counts, row.trade_count, vwaps, row.vwap, symbols, row.symbol)
			else:
				#For first row
				expected_time = dataframe_start_dt_utc
				expected_time_hour_min = expected_time.replace(second=0, microsecond=0)
				row_timestamp_hour_min = row.timestamp.replace(second=0, microsecond=0)
				while expected_time_hour_min < row_timestamp_hour_min:
					fill_lists(timestamps, expected_time, opens, row.open, highs, row.high, lows, row.low, closes, row.close, volumes, row.volume, trade_counts, row.trade_count, vwaps, row.vwap, symbols, row.symbol)
					expected_time += pd.Timedelta(time_delta)	
					expected_time_hour_min = expected_time.replace(second=0, microsecond=0)

				fill_lists(timestamps, row.timestamp, opens, row.open, highs, row.high, lows, row.low, closes, row.close, volumes, row.volume, trade_counts, row.trade_count, vwaps, row.vwap, symbols, row.symbol)				
				
			prev_row = row

		#End df iteration
		if prev_row != None:
			last_time_slot = prev_row.timestamp
			last_time_slot_hour_min = last_time_slot.replace(second=0, microsecond=0)
			if last_time_slot_hour_min < dataframe_end_dt_utc_hour_min:
				last_time_slot += pd.Timedelta(time_delta)
				fill_lists(timestamps, last_time_slot, opens, row.open, highs, row.high, lows, row.low, closes, row.close, volumes, row.volume, trade_counts, row.trade_count, vwaps, row.vwap, symbols, row.symbol)	
				last_time_slot_hour_min = last_time_slot.replace(second=0, microsecond=0)
			while last_time_slot_hour_min < dataframe_end_dt_utc_hour_min:
				last_time_slot += pd.Timedelta(time_delta)
				fill_lists(timestamps, last_time_slot, opens, row.open, highs, row.high, lows, row.low, closes, row.close, volumes, row.volume, trade_counts, row.trade_count, vwaps, row.vwap, symbols, row.symbol)	
				last_time_slot_hour_min = last_time_slot.replace(second=0, microsecond=0)


		df = pd.DataFrame({
    		'open': opens,
    		'high': highs,
    		'low': lows,
    		'close': closes,
    		'volume':volumes,
    		'trade_count':trade_counts,
    		'vwap':vwaps,
    		'symbol':symbols

		},index=timestamps)	
		df.index.name = 'timestamp'		

		return df



	"""
	The raw dataframe may ocassionally be missing rows entirely of one or more of the specified securities particularly during pre and post trading hours.
	We Want to return a complete dataframe with all the securities represented. The daily ohlcv data of the previous day are used to fill the missing data.
	Parameters:
		df (pandas.DataFrame): The raw dataframe which may be missing candlesticks for some securities.
		assets ([String]): A list of the securities in play sorted alphabetically by ticker symbol.
		start_date (pandas.Timestamp): Specifies the begining of the time range. 
		end_date (pandas.Timestamp): Specifies the end of the time range. 	
		time_delta (String):
		time_frame (Timeframe):	
		limit (Int): Number of candlsticks represented in dataframe.
	Returns:
		df (pandas.DataFrame): A copy of the raw dataframe with missing securities filled in. 
	"""
	def fill_missing_stocks(self, df, assets, start_date, end_date, time_delta, time_frame, limit):#Start and end dates are adjusted start and end for the relevant timeframe
		
		def fill_lists(timestamps, timestamp, opens, opn, highs, high, lows, low, closes, close, volumes, volume, trade_counts, trade_count, vwaps, vwap, symbols, symbol):
			timestamps.append(timestamp)
			opens.append(opn)
			highs.append(high)
			lows.append(low)
			closes.append(close)
			volumes.append(volume)
			trade_counts.append(trade_count)
			vwaps.append(vwap)
			symbols.append(symbol)		



		def iterate_assets(asset_index, timestamps, opens, opn, highs, high, lows, low, closes, close, volumes, volume, trade_counts, trade_count, vwaps, vwap, symbols, symbol):
			#insert some rows for that asset before inserting curr row	
			start = dataframe_start_dt_utc
			end = dataframe_end_dt_utc
			curr = start
			if limit == 1:#2:
				while curr <= end_date: 
					fill_lists(timestamps, curr, opens, opn, highs, high, lows, low, closes, close, volumes, volume, trade_counts, trade_count, vwaps, vwap, symbols, symbol)	
					curr += pd.Timedelta(time_delta)
			else:
				fill_lists(timestamps, curr, opens, None, highs, None, lows, None, closes, None, volumes, None, trade_counts, None, vwaps, None, symbols, symbol)				
			asset_index += 1	

			return asset_index


		#Dataframe returns dates in UTC. So need to convert from local time to UTC
		dataframe_start_dt_utc = start_date.tz_convert('UTC')
		dataframe_end_dt_utc = end_date.tz_convert('UTC')		

		df_indexed = df.reset_index()  #Make sure indexes pair with number of rows
		prev_row = None

		timestamps = []
		opens = []
		highs = []
		lows= []
		closes = []
		volumes = []
		trade_counts = []
		vwaps = []
		symbols = []
		asset_index = 0

		if len(df.index) == 0:		
			while asset_index < len(assets):
				#insert some rows for that asset before inserting curr row	
				asset_index = iterate_assets(asset_index, timestamps, opens, self.assets_ohlc[asset_index].get("open"), highs, self.assets_ohlc[asset_index].get("high"), lows, self.assets_ohlc[asset_index].get("low"), closes, self.assets_ohlc[asset_index].get("close"), volumes, self.assets_ohlc[asset_index].get("volume"), trade_counts, self.assets_ohlc[asset_index].get("trade_count"), vwaps, self.assets_ohlc[asset_index].get("vwap"), symbols, assets[asset_index])			

		else:#There are rows
			for row in df_indexed.itertuples():

				if row.Index > 0:
					if prev_row.symbol == row.symbol:
						pass			
					else:#End of an old symbol and start of a new symbol

						asset_index += 1#Move along assets list. New asset should be new row symbol otherwise, fill
						#New row
						while row.symbol != assets[asset_index]: #Next asset(s)'s  symbol(s) is(are) not same as that of current row.
							#insert some rows for that asset before inserting curr row	
							asset_index = iterate_assets(asset_index, timestamps, opens, self.assets_ohlc[asset_index].get("open"), highs, self.assets_ohlc[asset_index].get("high"), lows, self.assets_ohlc[asset_index].get("low"), closes, self.assets_ohlc[asset_index].get("close"), volumes, self.assets_ohlc[asset_index].get("volume"), trade_counts, self.assets_ohlc[asset_index].get("trade_count"), vwaps, self.assets_ohlc[asset_index].get("vwap"), symbols, assets[asset_index])
					
				else:
					#First row	
					while row.symbol != assets[asset_index]: #First asset(s)'s  symbol(s) is(are) not same as that of current row.
						#insert some rows for that asset before inserting curr row	
						asset_index = iterate_assets(asset_index, timestamps, opens, self.assets_ohlc[asset_index].get("open"), highs, self.assets_ohlc[asset_index].get("high"), lows, self.assets_ohlc[asset_index].get("low"), closes, self.assets_ohlc[asset_index].get("close"), volumes, self.assets_ohlc[asset_index].get("volume"), trade_counts, self.assets_ohlc[asset_index].get("trade_count"), vwaps, self.assets_ohlc[asset_index].get("vwap"), symbols, assets[asset_index])

				#Now insert current row
				fill_lists(timestamps, row.timestamp, opens, row.open, highs, row.high, lows, row.low, closes, row.close, volumes, row.volume, trade_counts, row.trade_count, vwaps, row.vwap, symbols, row.symbol)				

				prev_row = row

			#After last row, if there are still untouched assets. 
			#asset_index at this point should be index of last row's symbol since we must necessarily have gotten here via if row_index > 0 followed by if prev_row.symbol == row.symbol
			asset_index += 1#Move along assets list.
			#Asset index should now be one more than index of the last symbol encountered
			while asset_index < len(assets):
				asset_index = iterate_assets(asset_index, timestamps, opens, self.assets_ohlc[asset_index].get("open"), highs, self.assets_ohlc[asset_index].get("high"), lows, self.assets_ohlc[asset_index].get("low"), closes, self.assets_ohlc[asset_index].get("close"), volumes, self.assets_ohlc[asset_index].get("volume"), trade_counts, self.assets_ohlc[asset_index].get("trade_count"), vwaps, self.assets_ohlc[asset_index].get("vwap"), symbols, assets[asset_index])

		df = pd.DataFrame({
    		'open': opens,
    		'high': highs,
    		'low': lows,
    		'close': closes,
    		'volume':volumes,
    		'trade_count':trade_counts,
    		'vwap':vwaps,
    		'symbol':symbols

		},index=timestamps)	
		df.index.name = 'timestamp'		

		return df



	"""
	Retrieves a pandas dataframe for securities specified within the time range specified by start date and end date, at intervals specified by the timeframe.
	This dataframe may require some further processing to fill in missing data.
	Parameters
		config: Reference to config.py
		assets ([String]): A list of the securities in play sorted alphabetically by ticker symbol.
		time_delta (String):
		time_frame (TimeFrame):
		limit (Int): Number of candlsticks represented in dataframe.
		curr_date (pandas.Timestamp): Current minute.
	Returns:
		(pandas.DataFrame)
	"""
	def grab_df_and_fill_missing_stocks(self, config, assets, time_delta, time_frame, limit, curr_date):

		end_dt = curr_date
		start_dt = end_dt - pd.Timedelta(time_delta)*(limit-1)
		df = self.get_df(config, assets, time_frame, start_dt, end_dt)
		df = self.rearrange_rows_by_symbol(df, assets)
		df = self.fill_missing_stocks(df, assets, start_dt, end_dt, time_delta, time_frame, limit)
		
		return df




	def fill_time_slots(self, next_time_slot, timelist, temp_closes, temp_opens, temp_highs, temp_lows, temp_volumes, temp_vwaps, config, assets, time_delta, time_frame, limit, curr_date):

		df = self.grab_df_and_fill_missing_stocks(config, assets, time_delta, time_frame, limit, curr_date)
		#Go through each row of df
		df_indexed = df.reset_index() 
		prev_row = None
		row = None
		curr_stock_index = len(assets)-1#0
	
		symbols = []
		closes = []
		opens = []
		highs = []
		lows = []
		volumes = []
		vwaps = []

		for curr_row in df_indexed.itertuples():
			row = curr_row 
			symbols.append(row.symbol)
			closes.append(row.close)
			opens.append(row.open)
			highs.append(row.high)
			lows.append(row.low)
			volumes.append(row.volume)
			vwaps.append(row.vwap)

		symbols.reverse()
		closes.reverse()
		opens.reverse()
		highs.reverse()
		lows.reverse()
		volumes.reverse()
		vwaps.reverse()

		for row_index in range(0, len(symbols)):

			num_filled_time_slots = 0
			for i in range(0, len(temp_closes)):
				for j in range(0, len(temp_closes[i])):
					num_filled_time_slots += 1
					j += 1
				i += 1

			len_timelist = len(timelist) #This number should be same as number of filled timeslots
			assert num_filled_time_slots == len_timelist 

			if (row_index == 0) or (row_index != 0 and symbols[row_index - 1] != symbols[row_index]): #First row or symbol change

				if row_index != 0:
					curr_stock_index -= 1

			else: #Same symbol as last row
				pass


			#Insert the row
			if next_time_slot[curr_stock_index] < limit: #Stop filling if stock in question has reached limit
				#Should we insert in current child list of temp or prev one? Depends on next_time_slot for stock and length of prev one
				if next_time_slot[curr_stock_index] + 1 <= num_filled_time_slots:#len(temp_closes[-1]): 
					#Latest time slot for stock does not exceed index of already filled time slots
					#So find the bucket and time slot that corresponds with next_time_slot[stock_index] and insert into that bucket at the appropriate stock position
					next_time_slot_for_curr_stock_index = next_time_slot[curr_stock_index]
					bucket_index = 0
					time_slot_index = 0
					time_slot_count = 0
					for i in range(0, len(temp_closes)):
						break_outter_loop = False
						bucket_index = i
						for j in range(0, len(temp_closes[i])):
							time_slot_index = j
							time_slot_count += 1

							if next_time_slot_for_curr_stock_index + 1 == time_slot_count:
								break_outter_loop = True
								break 

						if break_outter_loop:
							break

					temp_closes[bucket_index][time_slot_index][curr_stock_index] = closes[row_index]
					temp_opens[bucket_index][time_slot_index][curr_stock_index] = opens[row_index]
					temp_lows[bucket_index][time_slot_index][curr_stock_index] = lows[row_index]
					temp_highs[bucket_index][time_slot_index][curr_stock_index] = highs[row_index]
					temp_volumes[bucket_index][time_slot_index][curr_stock_index] = volumes[row_index]
					temp_vwaps[bucket_index][time_slot_index][curr_stock_index] = vwaps[row_index]

				else: 
					#Latest time slot for stock exceeds number of timeslots already inserted. So create new one
					new_time_slot_close = [0] * len(assets)
					new_time_slot_open = [0] * len(assets)
					new_time_slot_low = [0] * len(assets)
					new_time_slot_high = [0] * len(assets)
					new_time_slot_volume = [0] * len(assets)
					new_time_slot_vwap = [0] * len(assets)

					new_time_slot_close[curr_stock_index] = closes[row_index]
					new_time_slot_open[curr_stock_index] = opens[row_index]
					new_time_slot_low[curr_stock_index] = lows[row_index]
					new_time_slot_high[curr_stock_index] = highs[row_index]
					new_time_slot_volume[curr_stock_index] = volumes[row_index]
					new_time_slot_vwap[curr_stock_index] = vwaps[row_index]
					temp_closes[-1].append(new_time_slot_close) 
					temp_opens[-1].append(new_time_slot_open)
					temp_lows[-1].append(new_time_slot_low)
					temp_highs[-1].append(new_time_slot_high)
					temp_volumes[-1].append(new_time_slot_volume)
					temp_vwaps[-1].append(new_time_slot_vwap)
					timelist.append(num_filled_time_slots) #The next index is the current length of list

			next_time_slot[curr_stock_index] += 1 #Increment latest time slot for stock in question by 1 now that row content has been added to lists
		return next_time_slot, timelist, temp_closes, temp_opens, temp_highs, temp_lows, temp_volumes, temp_vwaps



	def combine_buckets(self, list_of_buckets, col_name):
		
		combined_buckets = []

		for i in range(0, len(list_of_buckets)):
			for j in range(0, len(list_of_buckets[i])):
				combined_buckets.append(list_of_buckets[i][j])

		combined_buckets.reverse()

		#Remove Nans and 0s
		for i in range(0, len(combined_buckets)): #Every time slot
			for j in range(0, len(combined_buckets[i])): #Every stock
				if combined_buckets[i][j] == 0 or combined_buckets[i][j] == None:
					most_adjacent_value = 0
					k = i-1
					while k >= 0:
						if combined_buckets[k][j] != 0 and combined_buckets[k][j] != None:
							combined_buckets[i][j] = combined_buckets[k][j]
						k -= 1

				if combined_buckets[i][j] == 0 or combined_buckets[i][j] == None:
					k = i+1
					while k < len(combined_buckets):
						if combined_buckets[k][j] != 0 and combined_buckets[k][j] != None:
							combined_buckets[i][j] = combined_buckets[k][j]
						k += 1

				if combined_buckets[i][j] == 0 or combined_buckets[i][j] == None:
					combined_buckets[i][j] = self.assets_ohlc[j].get(col_name)

		return combined_buckets



	"""
	Replaces ohlc values stored in self.assets_ohlc. Originally, this list consisted of previous day's daily ohlc values. 
	But from here on out, it should consist of ohlc values of the most recent candlestick after the first dataframe is obtained.
	Parameters:
		comnined_list ([[[Float]]]):
		col_name (String): "close", "open", "high", "low", "volume", or "vwap"
	"""
	def update_asset_properties(self, combined_list, col_name):
		#Last row of combined list will now be assigned to asset properties
		for i in range(0, len(combined_list[0])): #Every stock (security)
			self.assets_ohlc[i][col_name] = combined_list[-1][i]



	"""
	Retrieves ohlcv data for securiteis specified for the specified timeframe. Continuously adds candlesticks to the growing dataframe untill
	the required number of candlesticks (limit), is obtained for each security in question. 
	Parameters:
		config: Reference to config.py
		assets ([String]): A list of the securities in play sorted alphabetically by ticker symbol.
		time_delta (String):
		time_frame (TimeFrame):
		limit (Int): Number of candlsticks represented in dataframe.
		curr_date (pandas.Timestamp): Current minute.	
	Returns:
		timelist ([Int]):
		combined_closes ([[Folat]]):
		combined_opens ([[Folat]]): 
		combined_highs ([[Folat]]): 
		combined_lows ([[Folat]]): 
		combined_volumes ([[Folat]]):
		combined_vwaps ([[Folat]]):
	"""
	def get_closes_opens_his_los_vols_vwaps(self, config, assets, time_delta, time_frame, limit, curr_date):
		if limit <= 3:
			df = self.grab_df_and_fill_missing_stocks(config, assets, time_delta, time_frame, limit, curr_date)
			
			end_dt = curr_date
			start_dt = end_dt - pd.Timedelta(time_delta)*(limit-1)			
			df = self.fill_missing_dates(df, time_delta, start_dt, end_dt)

			#num_rows = len(df.index)
			num_assets = len(assets)

			timelist = []
			[timelist.append(x) for x in df.index.tolist() if x not in timelist]
			return [
				timelist,
				self.unflatten(df.xs('close', axis=1), num_assets, limit),
				self.unflatten(df.xs('open', axis=1), num_assets, limit),
				self.unflatten(df.xs('high', axis=1), num_assets, limit),
				self.unflatten(df.xs('low', axis=1), num_assets, limit),
				self.unflatten(df.xs('volume', axis=1), num_assets, limit),
				self.unflatten(df.xs('vwap', axis=1), num_assets, limit)		
			]	

		else:
			timelist = []
			temp_closes = []
			temp_opens = []
			temp_highs = []
			temp_lows = []
			temp_volumes = []
			temp_vwaps = []

			df_iterations = 0
			next_time_slot = [0] * len(assets)
			all_stocks_reached_limit = False

			while not all_stocks_reached_limit: #We will continue to get last n = limit row dataframes till lists are full

				temp_closes.append([])
				temp_opens.append([])
				temp_highs.append([])
				temp_lows.append([])
				temp_volumes.append([])
				temp_vwaps.append([])

				next_time_slot, timelist, temp_closes, temp_opens, temp_highs, temp_lows, temp_volumes, temp_vwaps = self.fill_time_slots(next_time_slot, timelist, temp_closes, temp_opens, temp_highs, temp_lows, temp_volumes, temp_vwaps, config, assets, time_delta, time_frame, limit, curr_date)

				curr_date -= pd.Timedelta(time_delta)*(limit)
				df_iterations += 1

				all_stocks_reached_limit = True
				for i in range(0, len(assets)):
					if next_time_slot[i] < limit - 1:
						all_stocks_reached_limit = False
						break

			#Combine lists
			combined_closes = self.combine_buckets(temp_closes, "close")
			combined_opens = self.combine_buckets(temp_opens, "open")
			combined_highs = self.combine_buckets(temp_highs, "high")
			combined_lows = self.combine_buckets(temp_lows, "low")
			combined_volumes = self.combine_buckets(temp_volumes, "volume")
			combined_vwaps = self.combine_buckets(temp_vwaps, "vwap")				

			#Last row of combined buckets should replace asset ohlcv
			self.update_asset_properties(combined_closes, "close")
			self.update_asset_properties(combined_opens, "open")
			self.update_asset_properties(combined_highs, "high")
			self.update_asset_properties(combined_lows, "low")
			self.update_asset_properties(combined_volumes, "volume")
			self.update_asset_properties(combined_vwaps, "vwap")

			return [timelist, combined_closes, combined_opens, combined_highs, combined_lows, combined_volumes, combined_vwaps]			



	"""
	Calls the execute() function as often as developer deems necessary to execute the strategy.
	Parameters:
		strategy (Strategy): Instance of Strategy class.
		assets ([String]): A list of the securities in play sorted alphabetically by ticker symbol.
		start_trading_day (pandas.Timestamp): The timestamp representing the open of the trading day.
		end_trading_day (pandas.Timestamp): The timestamp representing the end of the trading day.
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
	def run(self, strategy, assets, start_trading_day, end_trading_day, _1min_time_delta, _1min_time_frame, _5min_time_delta, _5min_time_frame, _15min_time_delta, _15min_time_frame, day_time_delta, day_time_frame, **kwargs):	

		#Modify the number of minutes pre market
		trigger_time = start_trading_day - pd.Timedelta('0minutes')
		print("trigger_time "+str(trigger_time))

		kwargs['dt'].delete_files_at_start()

		limit = strategy.rows_limit

		_1min_time_frames, _1min_close_prices, _1min_open_prices, _1min_hi_prices, _1min_lo_prices, _1min_vols, _1min_vwaps = self.get_closes_opens_his_los_vols_vwaps(kwargs['config'], assets, _1min_time_delta, _1min_time_frame, limit, trigger_time)
		_5min_time_frames, _5min_close_prices, _5min_open_prices, _5min_hi_prices, _5min_lo_prices, _5min_vols, _5min_vwaps = self.get_closes_opens_his_los_vols_vwaps(kwargs['config'], assets, _5min_time_delta, _5min_time_frame, limit, trigger_time)
		_15min_time_frames, _15min_close_prices, _15min_open_prices, _15min_hi_prices, _15min_lo_prices, _15min_vols, _15min_vwaps = self.get_closes_opens_his_los_vols_vwaps(kwargs['config'], assets, _15min_time_delta, _15min_time_frame, limit, trigger_time)

		strategy._1min_time_frames, strategy._1min_close_prices, strategy._1min_open_prices, strategy._1min_hi_prices, strategy._1min_lo_prices, strategy._1min_vols, strategy._5min_time_frames, strategy._5min_close_prices, strategy._5min_open_prices, strategy._5min_hi_prices, strategy._5min_lo_prices, strategy._5min_vols, strategy._15min_time_frames, strategy._15min_close_prices, strategy._15min_open_prices, strategy._15min_hi_prices, strategy._15min_lo_prices, strategy._15min_vols = _1min_time_frames, _1min_close_prices, _1min_open_prices, _1min_hi_prices, _1min_lo_prices, _1min_vols, _5min_time_frames, _5min_close_prices, _5min_open_prices, _5min_hi_prices, _5min_lo_prices, _5min_vols, _15min_time_frames, _15min_close_prices, _15min_open_prices, _15min_hi_prices, _15min_lo_prices, _15min_vols

		kwargs['dt'].create_data_files(assets, limit, _1min_time_frames, _1min_open_prices, _1min_hi_prices, _1min_lo_prices, _1min_close_prices, _1min_vols, 'data_files/_1min_open.cvs', 'data_files/_1min_high.cvs', 'data_files/_1min_low.cvs', 'data_files/_1min_close.cvs', 'data_files/_1min_volume.cvs')
		kwargs['dt'].create_data_files(assets, limit, _5min_time_frames, _5min_open_prices, _5min_hi_prices, _5min_lo_prices, _5min_close_prices, _5min_vols, 'data_files/_5min_open.cvs', 'data_files/_5min_high.cvs', 'data_files/_5min_low.cvs', 'data_files/_5min_close.cvs', 'data_files/_5min_volume.cvs')
		kwargs['dt'].create_data_files(assets, limit, _15min_time_frames, _15min_open_prices, _15min_hi_prices, _15min_lo_prices, _15min_close_prices, _15min_vols, 'data_files/_15min_open.cvs', 'data_files/_15min_high.cvs', 'data_files/_15min_low.cvs', 'data_files/_15min_close.cvs', 'data_files/_15min_volume.cvs')		
	
		start_execution_time = trigger_time 
		curr_date = start_execution_time

		while(curr_date < end_trading_day):

			if curr_date < start_trading_day:
				#Premarket hours
				strategy.execute(self, assets, curr_date, start_execution_time, start_trading_day, end_trading_day, _1min_time_delta, _1min_time_frame, _5min_time_delta, _5min_time_frame, _15min_time_delta, _15min_time_frame, day_time_delta, day_time_frame, kwargs)
			else:
				#Live market hours
				strategy.execute(self, assets, curr_date, start_execution_time, start_trading_day, end_trading_day, _1min_time_delta, _1min_time_frame, _5min_time_delta, _5min_time_frame, _15min_time_delta, _15min_time_frame, day_time_delta, day_time_frame, kwargs)
			#Updates
			curr_date += pd.Timedelta(_1min_time_delta)#Increment time	

		print("THE END")


