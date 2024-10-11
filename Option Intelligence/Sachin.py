# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 11:19:34 2024

@author: Home
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 19:16:14 2024

@author: Home
"""
import urllib
import json
import pandas as pd
import datetime as dt
from datetime import date
from dateutil.relativedelta import relativedelta, TH
from MarketDataSocketClient import MDSocket_io
from UserConnection import connect_and_create_websocket,get_instrument_id,get_atm__strikePrice
from Connect import XTSConnect
from InteractiveSocketClient import OrderSocket_io
from SmartApi import SmartConnect
from SmartApi import SmartWebSocket
from AngelConnect import AngelConnection
import re
import time
from UserConnection import LegDetails,Option,process_orders,getGeeks,get_indexToken
from Compiler import compile_user_input

#-------------------Connections and API Data------------------#



#--------------------------------WisdoM Market Socket Connection----------#
#------------------------------Market Connection---------------#
MarketConnection=XTSConnect(MarketAPI, MarketSecret, source)
MarketResponse = MarketConnection.marketdata_login()

#------------------------------Broker User Connection----------#

User_Broker_Connection=connect_and_create_websocket(BrokerName,api_key,api_secretKey,username, pwd="none", authenticator="none")
Userresponse = User_Broker_Connection.interactive_login()

#----------------------------------------------------------------#
response = MarketConnection.get_ohlc(
    exchangeSegment="NSECM",
    exchangeInstrumentID="NIFTY 50",
    startTime='Jul 10 2024 091500',
    endTime='Jul 10 2024 141100',
    compressionValue=60)
print("OHLC: " + str(response))

