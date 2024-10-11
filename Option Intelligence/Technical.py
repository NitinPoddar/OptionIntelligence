# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 09:44:41 2024

@author: Home
"""

# Split the string into individual records
import datetime
from datetime import datetime
import pytz
import tzlocal
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_atr(data, period):
    data['high_low'] = data['high'] - data['low']
    data['high_close'] = (data['high'] - data['close'].shift(1)).abs()
    data['low_close'] = (data['low'] - data['close'].shift(1)).abs()
    
    true_range = data[['high_low', 'high_close', 'low_close']].max(axis=1)
    atr = true_range.rolling(window=period).mean()
    
    return atr


def supertrend(data, atr_period, multiplier, offset):
    atr = calculate_atr(data, atr_period)
    
    data['atr'] = atr
    data['upper_band'] = (data['high'] + data['low']) / 2 + (multiplier * atr)
    data['lower_band'] = (data['high'] + data['low']) / 2 - (multiplier * atr)

    super_trend = [0] * len(data)
    
    for i in range(len(data)):
        if i == 0:
            super_trend[i] = data['lower_band'][i]  # Initial value
        else:
            if data['close'][i] > super_trend[i - 1]:
                super_trend[i] = data['lower_band'][i]
            else:
                super_trend[i] = data['upper_band'][i]

            # Adjust if previous super trend was above the current close
            if super_trend[i - 1] > data['upper_band'][i] and data['close'][i] < data['upper_band'][i]:
                super_trend[i] = data['upper_band'][i]

            if super_trend[i - 1] < data['lower_band'][i] and data['close'][i] > data['lower_band'][i]:
                super_trend[i] = data['lower_band'][i]

    # Apply offset
    data['super_trend'] = [None] * len(data)
    #for i in range(len(data)):
       # if i + offset < len(data):
            #data['super_trend'][i + offset] = super_trend[i]

    return super_trend[-(offset+1)]

def ema(data, period,offset):
    alpha = 2 / (period + 1)
    closing_prices=data['close'].values
    initial_sma = sum(closing_prices[:period]) / period
    ema_values = [initial_sma]

    for price in closing_prices:
        new_ema = (price * alpha) + (ema_values[-1] * (1 - alpha))
        ema_values.append(new_ema)
    
    return ema_values[-(offset+1)]

def close(data,offset):
    return data['close'].values[-(offset+1)]


# Sample data
def EMACross(data,ema1,ema2,Get):
    alpha1 = 2 / (ema1 + 1)
    alpha2 = 2 / (ema2 + 1)
    closing_prices=data['close'].values
    fetch_prices=data[Get].values
    initial_sma1 = sum(closing_prices[:ema1]) / ema1
    ema_values1 = [initial_sma1]
    initial_sma2 = sum(closing_prices[:ema2]) / ema2
    ema_values2 = [initial_sma2]
    flag=1
    i=1
    CrossedValue=0
    for price in closing_prices:
        new_ema1 = (price * alpha1) + (ema_values1[-1] * (1 - alpha1))
        ema_values1.append(new_ema1)
        new_ema2 = (price * alpha2) + (ema_values2[-1] * (1 - alpha2))
        ema_values2.append(new_ema2)
        if ema_values1[i-1]>ema_values2[i-1] and flag==1:
            CrossedValue=fetch_prices[i-1]
            flag=2
       
        i=i+1
    
    return CrossedValue

def DaystoExpiry(Expiry):
    # Define the date format
    date_format = "%d%b%Y"  # Format for "09OCT2024"
    
    # Parse the expiry date
    expiry_date = datetime.strptime(Expiry, date_format)
    
    # Get today's date
    today = datetime.now()
    
    # Calculate the difference
    difference = (expiry_date - today).days
    
    return difference

def is_current_time_greater_than(target_time_str):
    # Define the time format
    time_format = "%H:%M"  # Format for "HH:MM"
    
    # Parse the target time
    target_time = datetime.strptime(target_time_str, time_format).time()
    
    # Get the current time
    current_time = datetime.now().time()
    
    # Check if current time is greater than target time
    return current_time > target_time



# Split the string into individual records


def moving_average(data, window_size):
    closes = [entry['close'] for entry in data]
    ma = []
    for i in range(len(closes)):
        if i + 1 < window_size:
            ma.append(None)  # Not enough data points to fill the window
        else:
            window = closes[i + 1 - window_size:i + 1]
            ma.append(sum(window) / window_size)
    return ma

def HighestHighValue(data, NumberofCandles,offset):
    # Calculate the highest high value with the given offset
    if len(data) > NumberofCandles + offset:
        highest_high = data['high'].iloc[-(NumberofCandles + offset):-offset].max()
    else:
        highest_high = data['high'].max()  # Fallback if not enough data
    return highest_high



def OhlcChart(data_list):
    
    timestamps = [entry['timestamp'] for entry in data_list]
    opens = [entry['open'] for entry in data_list]
    highs = [entry['high'] for entry in data_list]
    lows = [entry['low'] for entry in data_list]
    closes = [entry['close'] for entry in data_list]
    
    plt.figure(figsize=(10, 6))
    
    plt.plot(timestamps, opens, label='Open')
    plt.plot(timestamps, highs, label='High')
    plt.plot(timestamps, lows, label='Low')
    plt.plot(timestamps, closes, label='Close')
    
    plt.xlabel('Timestamp')
    plt.ylabel('Price')
    plt.title('Stock OHLC Data')
    plt.legend()
    return plt
    

