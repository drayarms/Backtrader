This tutorial assumes that you have an Alpaca trading account (you will need to obtain your own unique Alpaca API key ID and secret key) and are subscribed to Alpaca's SIP historical data feed. If you are not subscribed to SIP, you still have access to Alpaca's IEX data feed. However, keep in mind that IEX provides much less accurate data. You also need to have installed Alpaca's trade API which this backtrading library is built on. 

```
pip3 install alpaca-trade-api
```

Our backtrader's functionality relies on a number of Python libraries listed below.

### numpy:
```
pip3 install python3-numpy
```
We will be working alot with lists containing huge amounts of data (ohlcv data for multiple securities spanning multiple candlesticks). Numpy comes in quite handy in performing mathematical operations over such lists especially when computing various trading indicators.

### pandas:
```
pip3 install python3-pandas
```
Pandas facilitates computations within huge dataframes such as the dataframes containing ohlcv data we will be fetching on a regular basis throughout our simulation.

### matplotlib:
```
pip3 install python3-matplotlib
```
Useful for plotting charts.

### mpl-finance
```
pip3 install --upgrade mplfinance
```
Useful for plotting candlesticks on our charts.



We will walk through the most significant portions of the library that require you to get your stretegy up and running in no time. 


## config.py

Let's break down the components of config.py

```
import alpaca_trade_api as tradeapi
```
We need to include Alpaca's trade api which is what this backtester library is built on. 

```
APCA_API_BASE_URL= "https://paper-api.alpaca.markets"
```
The base url is the endpoint of the REST API. After you have successfully built your winning strategy and are ready to deploy your algorithm for live trading, you would have to switch the base url to "https://api.alpaca.markets", the live trading endpoint.

```
APCA_API_KEY_ID= "XXXXXXXXXXXXXXXXXXXX"
APCA_API_SECRET_KEY= "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```
You need to supply your own unique auto generated API key and secret key. 

```
api = tradeapi.REST(
    base_url=APCA_API_BASE_URL,
    key_id=APCA_API_KEY_ID,
    secret_key=APCA_API_SECRET_KEY
)

from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
```
The REST object has a number of methods that come in handy for obtaining information about your account including your account equity balance, market pricing etc. For our purposes however, we will mostly be utilizing this object's get_bars() method to get ohlcv candlesticks for our securities in play. We will also be utilizing the TimeFrame and TimeFrameUnit objects for pulling ohlcv dataframes.


## simulator.py
This is the entry point to our program. Let's dive into this file to explain some setups.

```
TIMEZONE = timezone('US/Pacific')
```
You would need to change the timezone object to your own timezone.


On the command line interface, the program should be trigerred thus:
```
python3 simulator.py 
```

In the main() function, we define time deltas and time frames for 1, 5, 15 minute candlesticks as well as 1 day candelsticks. We will use the time delta objects to compute the time differences between two specified points on the timeline. Time frame objects are crucial components of Alpacs's REST API's get_bars() function which returns ohlcv data for a specified set of securities and for the duration of a specified period.

In the run() function, you need to modify the first two arguments to indicate the time duration during which you want to run your strategy. So say for instance you wanted to run you strategy for the entire trading day of November 9th 2022, your run function should look like this:
```
run(pd.Timestamp('2022-11-09 06:30',tz=TIMEZONE), pd.Timestamp('2022-11-09 13:00',tz=TIMEZONE), _1min_time_delta, _1min_time_frame, _5min_time_delta, _5min_time_frame, _15min_time_delta, _15min_time_frame, day_time_delta, day_time_frame)
```
 Note that 6:60 to 13:00 is the duration of a typical trading day in the Pacific standard time zone. So you would have to adjust the hours accordingly to reflect trading hours in your timezone. So for instance, if you live in New York, your trading day goes from 9:30 to 16:00.

In the run() function, you should specify which securities you want to use for your strategy. All the securities should be listed in a list which is assigned to the ```assets``` variable. The list is sorted alphabetically for convenience. We create an instance of Backtrader class. We then assign to the ```assets_ohlc``` attribute of our ```backtrader``` instance, daily ohclv information from the trading day prior to our specified trading day. We need this data to substitute missing time slots which typically happens for low float stocks especially during pre-trading hours. Each security under consideration will have their ohclv data in a dictionary and the dictionaries will appear in alphabetical order by their ticker symbols. 

Finally, we create instances of Strategy, Indicator, Plot, and Data classes. All the above class instances along with other relevant data are passed as arguments in the backtrader.run() function.

You should specify the second argument (rows_limit) of your Strategy instance. This will be the number of rows (candlesticks) returned each time we request a dataframe of ohlcv data. The number of rows you want to return should be completely up to you. If you intend to the RSI in you stategy for example, then the number of candlestikcs you want returned should be no less than 15 since the RSI is typically computed with data from the last 15 candlesticks. 


## backtrader.py

The backtrader class plays two main roles. 
1) The run() function loops minute by minute through the specified start of your trading session to the end of it.  In this example, the execute() method of our Strategy class is called each minute.  It is totally up to you though to modify the run() function in Backtrader, to control the frequency at which execute() gets called. The execute() method is where you will implement your strategy. 
2)Various helper functions that return pandas dataframes of ohlcv data for specified securities within a specified time duration. These functions transform the returned dataframes into simpler to use lists.  

You can modify the following line
```
trigger_time = start_date - pd.Timedelta('0minutes')
```
to specify how many pre-market minutes you want included as part of your strategy.


## strategy.py
The execute() function is where the magic happens. Recall,  this function is called from Bactrader class, as many times a minute as you might require for your strategy.

ohclv data for all timeframes(1, 5, 15 minutes), for each security in play is provided to make things a lot easier for you.  For example, ```_5min_close_prices_read_from_file``` is a list of the last n 5 minute open prices, where n is the number of rows returned (which you specified by assigning the rows_limit attribute of your stratery instance). The first row would represent the first candlestick, the second row the second candlestick and so on. The columns represent the securities in play which you specified in simulator.py. The columns appear in alphabetical order by ticker name. ```_5min_close_price``` represents the most recent candlestick (ie the last row of ```_5min_close_prices_read_from_file```).  Collectively, all the lists provided for you are sufficient to compute just about any indicator you might wish to use for your strategy. In this example, we compute the ema12 at the 5 minute tiemframe. We also pass candlestick data to our instance of plot class, where we will ultimately plot the candlesticks on a chart alongside the moving averages we compute.

After your strategy has run the entire simulation, you may desire to visualize the candlestick and moving averages plotted on a chart. 


## plot.py
in the plot_full_chart() function, we call the candlesick_ohlc function impoted form mpl_finance to plot green and red bars on a chart. 
candlestick_ohlc(ax1, self.ohlc[i][2], width=40, colorup='green', colordown='red')
The second function specifies which timeframe we want to plot.
```self.ohlc[i][0]``` represents 1 minute timeframe
```self.ohlc[i][1]``` represents 5 minute timeframe
```self.ohlc[i][2```] represents 15 minute timeframe

Similarly, in plotting moving averages, we specify which timeframes we want to plot moving averages for. For example,
```ax1.plot(self.time_list[i][0], self.ema12_list[i][0])``` plots the 1 minute 12 ema
```ax1.plot(self.time_list[i][0], self.ema12_list[i][1])``` plots the 5 minute 12 ema
```ax1.plot(self.time_list[i][2], self.ema12_list[i][2])``` plots the 15 minute 12 ema


