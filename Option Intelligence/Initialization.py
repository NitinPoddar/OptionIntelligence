# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 20:37:25 2024

@author: Nitin
"""

import urllib
import json
import pandas as pd
import datetime as dt
from datetime import date
from dateutil.relativedelta import relativedelta, TH
#from MarketDataSocketClient import MDSocket_io
from UserConnection import connect_and_create_websocket,get_instrument_id,get_atm__strikePrice,getExchangeSegmentNo
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

instrument_url="https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
response=urllib.request.urlopen(instrument_url)
instrument_List=json.loads(response.read())


#--------------------------------Wisdom Market Socket Connection----------#
MarketAPI="3693365223fe4245cdf395"
MarketSecret="Yrss334$cu"
source="WEBAPI"

MarketAPI="ecebb11fd01c27761c2d79"
MarketSecret="Ifyi021@uz"
source="WEBAPI"

#------------------------------Market Connection---------------#
MarketConnection=XTSConnect(MarketAPI, MarketSecret, source)
MarketResponse = MarketConnection.marketdata_login()
set_marketDataToken = MarketResponse['result']['token']
set_muserID = MarketResponse['result']['userID']
print("Login: ", MarketResponse)
# Connecting to Marketdata socket
#soc = MDSocket_io(set_marketDataToken, set_muserID)
# Instruments for subscribing
#---------------------------------------------------------------------#
#---1502 gives market depth
#---1505 gives candle data
#----1507 gives market current status
#----1510 Open Interest
#-----1512 LTP


#------------------------------Broker User Connection----------#
BrokerName= "Wisdom Capital"
api_key="8f1269a135ba0a3a5b5962"
api_secretKey="Whux471#A9"
username="WD4612"

BrokerName= "Wisdom Capital"
api_key="5a83794ac0a799b7547773"
api_secretKey="Hnnj287@CH"
username="WC23558"

User_Broker_Connection=connect_and_create_websocket(BrokerName,api_key,api_secretKey,username, pwd="none", authenticator="none")
Userresponse = User_Broker_Connection.interactive_login()
set_interactiveToken = Userresponse['result']['token']
set_iuserID = Userresponse['result']['userID']
print("Login: ", Userresponse)


#-------------------------Angel Market for Geek Information------#
AngelMarketConnect=AngelConnection("337918")

#----------------------------------------------------------------#
response = User_Broker_Connection.place_order(
    exchangeSegment="NSEFO",
    exchangeInstrumentID=54767,
    productType="NRML",
    orderType='LIMIT',
    orderSide='Sell',
    timeInForce='DAY',
    disclosedQuantity=0,
    orderQuantity=25,
    limitPrice=114,
    stopPrice=0,
    orderUniqueIdentifier="KohliOption2",
    clientID="WD4612")
print("Place Order: ", response)