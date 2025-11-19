from backtesting import Strategy
import pandas as pd
import pandas_ta as ta
import numpy as np

def rsi_wrapper(close_array, length=14):
    close_series = pd.Series(close_array)
    rsi_series = ta.rsi(close_series, length=length)
    if rsi_series is None: return np.full_like(close_array, np.nan)
    return rsi_series.values

def sma_wrapper(data_array, length=20):
    data_series = pd.Series(data_array)
    sma_series = ta.sma(data_series, length=length)
    if sma_series is None: return np.full_like(data_array, np.nan)
    return sma_series.values

class StratDailyMR(Strategy):
    
    trend_sma_period = 200
    rsi_period = 2
    rsi_oversold_level = 10
    exit_sma_period = 5
    fixed_size = 1.0
    
    def init(self):
        self.sma_trend = self.I(sma_wrapper, 
                                self.data.Close, 
                                length=self.trend_sma_period)
        
        self.rsi = self.I(rsi_wrapper, 
                          self.data.Close, 
                          length=self.rsi_period)
        
        self.sma_exit = self.I(sma_wrapper,
                               self.data.Close,
                               length=self.exit_sma_period)

    def next(self):
        
        if len(self.rsi) < self.rsi_period or \
           len(self.sma_trend) < self.trend_sma_period or \
           len(self.sma_exit) < self.exit_sma_period:
            return

        current_close = self.data.Close[-1]
        current_rsi = self.rsi[-1]
        current_trend_sma = self.sma_trend[-1]
        current_exit_sma = self.sma_exit[-1]

        if self.position:
            if current_close > current_exit_sma:
                self.position.close()
                return

        if not self.position:
            is_uptrend = current_close > current_trend_sma
            is_oversold = current_rsi < self.rsi_oversold_level
            
            if is_uptrend and is_oversold:
                self.buy(size=self.fixed_size)