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
from UserConnection import LegDetails,Option,SmartOrder
from Compiler import compile_user_input

#-------------------Connections and API Data------------------#

instrument_url="https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
response=urllib.request.urlopen(instrument_url)
instrument_List=json.loads(response.read())

AngelMarketConnect=AngelConnection("995333")
LegName="A"
Script="NIFTY"
Exchange="NSE"
Counter="1"

MarketAPI="d6f4261dd80f4a0e8adc80"
MarketSecret="Rhdp825@bU"
source="WEBAPI"

MarketConnection=XTSConnect(MarketAPI, MarketSecret, source)
response = MarketConnection.marketdata_login()

BrokerName= "Wisdom Capital"
api_key="865e5797741bc21838e722"
api_secretKey="Luur308@gK"
username="WD3868"

User_Broker_Connection=connect_and_create_websocket(BrokerName,api_key,api_secretKey,username, pwd="none", authenticator="none")
response = User_Broker_Connection.interactive_login()


#-------------------------------Python Version---------#
Leg= LegDetails(Script,instrument_List,LegName,Exchange,AngelMarketConnect)       

Leg1=Option(Leg,MarketConnection,AngelMarketConnect,OrderSide="BUY",LimitPrice=10,StrikePrice="SpotATM",Delta=0,Vega=0,Expiry="11JUL2024",orderType="Limit",productType="NRML",instrumentlist=instrument_List,Sequence=0,Steps=0,Quantity=25,OptionType="CE",timeInForce="DAY")
Leg1['Counter']=Counter
Counter="2"
Leg2=Option(Leg,MarketConnection,AngelMarketConnect,OrderSide="Sell",LimitPrice=0,StrikePrice="SpotATM",Delta=0,Vega=0,Expiry="11JUL2024",orderType="Market",productType="NRML",instrumentlist=instrument_List,Sequence=0,Steps=0,Quantity=25,OptionType="PE",timeInForce="DAY")
Leg2['Counter']=Counter
Counter="3"
Leg3=Option(Leg,MarketConnection,AngelMarketConnect,OrderSide="Sell",LimitPrice=0,StrikePrice="SpotATM",Delta=0,Vega=0,Expiry="11JUL2024",orderType="LimitThanMarket",productType="NRML",instrumentlist=instrument_List,Sequence=10,Steps=0.05,Quantity=25,OptionType="CE",timeInForce="DAY")
Leg3['Counter']=Counter

Option(LegDetails('NIFTY', instrument_List, 'A', 'NSE', AngelMarketConnect), MarketConnection, AngelMarketConnect, OrderSide='Sell', LimitPrice=0.0, StrikePrice=24300, Delta=0.0, Vega=0.0, Expiry='11JUL2024', orderType='Market', productType='NRML', instrumentlist=instrument_List, Sequence=0.0, Steps=0.0, Quantity=25.0, OptionType='PE', timeInForce='DAY')


EntryLeg = pd.concat([Leg1, Leg2, Leg3], axis=0)
#---------------------------IDE Version-----------------------------#
# Example user input with mixed StrikePrice types and orderType with parameters
user_input = """
Create Leg="A" Script="NIFTY" Exchange="NSE"
Leg="A",Counter="1",OrderSide="BUY",StrikePrice="SpotATM",Expiry="11JUL2024",orderType=Limit,LimitPrice=10,productType="NRML",Quantity=25,OptionType="CE",timeInForce="DAY"
Leg="A",Counter="2",OrderSide="Sell",StrikePrice=24300,Expiry="11JUL2024",orderType="Market",productType="NRML",Quantity=25,OptionType="PE",timeInForce="DAY"
Leg="A",Counter="3",OrderSide="Sell",StrikePrice="24100",Expiry="11JUL2024",orderType="LimitThanMarket",Sequence=10,Steps=0.05,productType="NRML",Quantity=25,OptionType="CE",timeInForce="DAY"
"""
# Compile user input into Python code
EntryLeg = compile_user_input(user_input)
print(compiled_result)
#-----------------------------Executing Entry Leg------------------------------------#
EntryLeg = process_orders(EntryLeg, User_Broker_Connection, username, BrokerName)



