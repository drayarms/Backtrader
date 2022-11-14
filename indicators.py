"""
Author: Ngusum Akofu
Date Created: Nov 17, 2021
"""

import numpy as np

class Indicators:
	
	def __init__(self, num_assets):

		self._1min_ema12 = []
		self._5min_ema12 = []
		self._15min_ema12 = []


	def last_n_rows(self, flattened_df, n):
		return flattened_df[-n:]

	def compute_sma(self, arr):
		return np.mean(arr, axis=0)

	

	def compute_ema(self, price, prev_ema, N):
		k = 2/(N+1)
		return np.add(np.multiply(np.subtract(price, prev_ema), k), prev_ema)


	
	def compute_exponential_moving_averages(self, close_price, sma12, _ema12):

		prev_ema12 = _ema12	

		if len(_ema12) == 0:#At first 1 min, 5min, or 15min

			prev_ema12 = sma12

		ema12 = self.compute_ema(close_price, prev_ema12, 12)

		return ema12



	
	def generate_indicators(self, close_prices, ema12):
	
		close_price = close_prices[-1]
		close_price12 = close_prices[-12:] #kwargs['bt'].last_n_rows(close_prices, 12)
		sma12 = self.compute_sma(close_price12)

		ema12 = self.compute_exponential_moving_averages(close_price, sma12, ema12)

		return ema12



