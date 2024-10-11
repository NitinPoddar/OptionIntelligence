# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 22:01:15 2024

@author: Home
"""
from datetime import datetime
import urllib
import json
import pandas as pd
import datetime as dt
from datetime import date
from dateutil.relativedelta import relativedelta, TH
from Connect import XTSConnect
from MarketDataSocketClient import MDSocket_io

# MarketData API Credentials
API_KEY = "d6f4261dd80f4a0e8adc80"
API_SECRET = "Rhdp825@bU"
source = "WEBAPI"

# Initialise
xt = XTSConnect(API_KEY, API_SECRET, source)

# Login for authorization token
response = xt.marketdata_login()


import yfinance as yf

# Get the data for the stock AAPL
data = yf.download('RELIANCE','2019-01-01','2014-07-26')


#------Nifty Data------#
from nselib import capital_market
import pandas as pd
from_date_str = '05-05-2019'
to_date_str = '15-07-2024'
index_data = capital_market.index_data(index='Nifty 50', from_date=from_date_str, to_date=to_date_str)
index_data['TIMESTAMP'] = pd.to_datetime(index_data['TIMESTAMP'], format='%d-%m-%Y')
index_data = index_data.sort_values('TIMESTAMP').reset_index(drop=True)
index_data
index_data.to_csv("C:/Users/Home/Desktop/Personal Projects/Stocks/NIFTY.csv", sep=',', index=False, encoding='utf-8')

tickers={"INFY","HDFCBANK","ICICIBANK","LT","ITC","RELIANCE","POWERGRID","SBIN",
"BhartiARTL",
"TCS",
"AxisBank",
"M&M",
"KOTAKBANK",
"HINDUNILVR",
"BAJFinance",
"NTPC",
"Tatamotors",
"TATASTEEL",
"TITAN",
"GRASIM",
"DRREDDY"}
from jugaad_data.nse import stock_df
Path="C:/Users/Home/Desktop/Personal Projects/Stocks/"
for ticker in tickers:

ticker="DRREDDY"
from jugaad_data.nse import stock_df
ExportFile=Path+ticker+'.csv'
stock_df = stock_df(symbol=ticker, 
                                from_date=date(2018,10,12), 
                                to_date=date(2024,7,15), 
                                series="EQ")
stock_df.to_csv(ExportFile, index=False, encoding='utf-8')



# Store the token and userid
set_marketDataToken = response['result']['token']
set_muserID = response['result']['userID']

response = xt.get_ohlc(
    exchangeSegment="NSECM",
    exchangeInstrumentID="NIFTY 50",
    startTime='Jul 10 2024 091500',
    endTime='Jul 15 2024 141100',
    compressionValue=60)
print("OHLC: " + str(response))



response = xt.get_ohlc(
    exchangeSegment=xt.EXCHANGE_NSECM,
    exchangeInstrumentID='22',
    startTime='Dec 16 2019 090000',
    endTime='Dec 18 2019 150000',
    compressionValue=1)
print("OHLC: " + str(response))

