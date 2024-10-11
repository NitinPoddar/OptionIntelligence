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


#--------------------------------WisdoM Market Socket Connection----------#
MarketAPI="d6f4261dd80f4a0e8adc80"
MarketSecret="Rhdp825@bU"
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
soc = MDSocket_io(set_marketDataToken, set_muserID)
# Instruments for subscribing
#---------------------------------------------------------------------#
#---1502 gives market depth
#---1505 gives candle data
#----1507 gives market current status
#----1510 Open Interest
#-----1512 LTP


#------------------------------Broker User Connection----------#
BrokerName= "Wisdom Capital"
api_key="865e5797741bc21838e722"
api_secretKey="Luur308@gK"
username="WD3868"

BrokerName= "Wisdom Capital"
api_key="5a83794ac0a799b7547773"
api_secretKey="Hnnj287@CH"
username="WC23558"

User_Broker_Connection=connect_and_create_websocket(BrokerName,api_key,api_secretKey,username, pwd="none", authenticator="none")
Userresponse = User_Broker_Connection.interactive_login()
set_interactiveToken = Userresponse['result']['token']
set_iuserID = Userresponse['result']['userID']
print("Login: ", Userresponse)

# Connecting to Interactive socket
socUser = OrderSocket_io(set_interactiveToken, set_iuserID)
response = User_Broker_Connection.get_position_daywise(clientID=username)
print("Position by Day: ", response)

"""Get Position by NET Request"""
response = User_Broker_Connection.get_position_netwise(clientID=username)
print("Position by Net: ", response)
response = User_Broker_Connection.get_dealerposition_daywise(clientID=username)
print("Dealer Position by Net: ", response)

#-------------------------Angel Market for Geek Information------#
AngelMarketConnect=AngelConnection("123998")

#----------------------------------------------------------------#
ScriptToken=get_indexToken("BANKEX")

response = MarketConnection.get_ohlc(
    exchangeSegment="BSECM",
    exchangeInstrumentID="BANKEX",
    startTime='Sep 22 2024 091500',
    endTime='Sep 23 2024 152000',
    compressionValue=300)
print("OHLC: " + str(response))


#-------------------------------Python Version---------#
LegName="A"
Script="BANKNIFTY"
Exchange="NSE"
Leg= LegDetails(Script,instrument_List,LegName,Exchange,AngelMarketConnect)       
Expiry="15JUL2024"
Quantity=15
Counter="1"
Leg1=Option(LegDetails(Script,instrument_List,LegName,Exchange,AngelMarketConnect),MarketConnection,AngelMarketConnect,OrderSide="SELL",StrikePrice="SynthATM",delta=0,vega=0,gamma=0,impliedVolatility=0,Expiry=Expiry,orderType="LimitThanMarket",LimitPrice=0,productType="NRML",instrumentlist=instrument_List,Sequence=10,Steps=0.05,Quantity=Quantity,OptionType="PE",timeInForce="DAY")
Leg1['Counter']=Counter
#EntryLeg1 = process_orders(Leg1, User_Broker_Connection, username, BrokerName)

Counter="2"
Leg2=Option(LegDetails(Script,instrument_List,LegName,Exchange,AngelMarketConnect),MarketConnection,AngelMarketConnect,OrderSide="SELL",LimitPrice=0,StrikePrice="SynthATM",delta=0,vega=0,gamma=0,impliedVolatility=0,Expiry=Expiry,orderType="LimitThanMarket",productType="NRML",instrumentlist=instrument_List,Sequence=10,Steps=0.05,Quantity=Quantity,OptionType="CE",timeInForce="DAY")
Leg2['Counter']=Counter

Counter="3"
#Temp1=getGeeks(AngelMarketConnect,ticker="NIFTY",Expiry="11JUL2024",GeekType="delta",StrikePrice="SpotATM",instrumentlist=instrument_List,Exchange="NFO",OptionType="CE")
#Temp2=Temp1-0.11
Temp2=Leg['Spot']+(Leg1['EndPrice']+Leg2["EndPrice"])

Leg3=Option(LegDetails(Script,instrument_List,LegName,Exchange,AngelMarketConnect),MarketConnection,AngelMarketConnect,OrderSide="BUY",LimitPrice=0,StrikePrice=Temp2.values[0],delta=0,vega=0,gamma=0,impliedVolatility=0,Expiry=Expiry,orderType="LimitThanMarket",productType="NRML",instrumentlist=instrument_List,Sequence=10,Steps=0.05,Quantity=Quantity,OptionType="CE",timeInForce="DAY")
Leg3['Counter']=Counter

Counter="4"
#Temp1=getGeeks(AngelMarketConnect,ticker="NIFTY",Expiry="11JUL2024",GeekType="delta",StrikePrice="SpotATM",instrumentlist=instrument_List,Exchange="NFO",OptionType="PE")
#Temp3=Temp1+0.11
Temp3=Leg['Spot']-(Leg1['EndPrice']+Leg2["EndPrice"])

Leg4=Option(LegDetails(Script,instrument_List,LegName,Exchange,AngelMarketConnect),MarketConnection,AngelMarketConnect,OrderSide="BUY",LimitPrice=0,StrikePrice=Temp3[0],delta=0,vega=0,gamma=0,impliedVolatility=0,Expiry=Expiry,orderType="LimitThanMarket",productType="NRML",instrumentlist=instrument_List,Sequence=10,Steps=0.05,Quantity=Quantity,OptionType="PE",timeInForce="DAY")
Leg4['Counter']=Counter

EntryLeg = pd.concat([Leg1, Leg2, Leg3,Leg4], axis=0)
EntryLeg = EntryLeg.sort_values(by='orderSide')
Instruments = []

for j in range(0,len(EntryLeg)):
     data_dict= {'exchangeSegment': getExchangeSegmentNo(EntryLeg['exchangeSegment'].iloc[j]), 'exchangeInstrumentID':EntryLeg['exchangeInstrumentID'].iloc[j]}
     Instruments.append(data_dict)

el = socUser.get_emitter()
el.on('position', on_position)
socUser.connect()

Instrument=[ {'exchangeSegment': 2, 'exchangeInstrumentID':"142647"},
            {'exchangeSegment': 2, 'exchangeInstrumentID':"142646"}]
def on_connect():
    """Connect from the socket."""
    print('Market Data Socket connected successfully!')
    # # Subscribe to instruments
    print('Sending subscription request for Instruments - \n' + str(Instruments))
    response = MarketConnection.send_subscription(Instrument, 1501)
    print('Sent Subscription request!')
    print("Subscription response: ", response)


def on_message1512_json_partial(data):
    print('I received a 1512 Level1,LTP message!' + data)

soc.on_connect = on_connect
soc.on_message1512_json_partial = on_message1512_json_partial


# Event listener
el = soc.get_emitter()
el.on('connect', on_connect)
el.on('1512-json-partial', on_message1512_json_partial)
soc.connect()


ProcessOrder = process_orders(EntryLeg, User_Broker_Connection, username, BrokerName)
EntryLeg = EntryLeg.reset_index(drop=True)
FinalLeg_shitesh=pd.concat([EntryLeg, pd.DataFrame(ProcessOrder)],axis=1)



response = User_Broker_Connection.get_order_history(appOrderID='1210912997',clientID=username)
print("Order History: ", response)
response = User_Broker_Connection.cancel_order(
    appOrderID='1210929745',
    orderUniqueIdentifier='454845',
    clientID=username)
print("Cancel Order: ", response)



#---------------------------IDE Version-----------------------------#
# Example user input with mixed StrikePrice types and orderType with parameters
user_input = """
Create Leg="A" Script="NIFTY" Exchange="NSE"
Leg="A",Counter="1",OrderSide="SELL",StrikePrice="SpotATM",Expiry="11JUL2024",orderType="Limit",LimitPrice=10,productType="NRML",Quantity=25,OptionType="CE",timeInForce="DAY"
Leg="A",Counter="2",OrderSide="SELL",StrikePrice=24300,Expiry="11JUL2024",orderType="Market",productType="NRML",Quantity=25,OptionType="PE",timeInForce="DAY"
Temp1=getGeeks(ticker="NIFTY",Expiry="11JUL2024",GeekType="Delta",StrikePrice="SpotATM",Exchange="NFO",OptionType="CE")
Temp2=Temp1-0.11
Leg="A",Counter="3",OrderSide="BUY",Delta=Temp2,Expiry="11JUL2024",orderType="LimitThanMarket",Sequence=10,Steps=0.05,productType="NRML",Quantity=25,OptionType="CE",timeInForce="DAY"
Temp3=Temp1+0.11
Leg="A",Counter="4",OrderSide="BUY",Delta=Temp3,Expiry="11JUL2024",orderType="LimitThanMarket",Sequence=10,Steps=0.05,productType="NRML",Quantity=25,OptionType="PE",timeInForce="DAY"

"""
user_input = """
Create Leg="A" Script="BANKNIFTY" Exchange="NSE"
Temp1=getGeeks(ticker="BANKNIFTY",Expiry="10JUL2024",GeekType="delta",StrikePrice="SpotATM",Exchange="NFO",OptionType="PE")
Temp3=Temp1+0.11
Leg="A",Counter="4",OrderSide="BUY",Delta=Temp3,Expiry="10JUL2024",orderType="LimitThanMarket",Sequence=10,Steps=0.05,productType="NRML",Quantity=15,OptionType="PE",timeInForce="DAY"
"""


# Compile user input into Python code
EntryLeg = compile_user_input(user_input)
#-----------------------------Executing Entry Leg------------------------------------#
EntryLeg = process_orders(EntryLeg, User_Broker_Connection, username, BrokerName)

# Example usage
user_input = """
Create Leg="A" Script="NIFTY" Exchange="NSE"
Leg="A",Counter="1",OrderSide="SELL",StrikePrice="SpotATM",Expiry="11JUL2024",orderType="Limit",LimitPrice=10,productType="NRML",Quantity=25,OptionType="CE",timeInForce="DAY"
Leg="A",Counter="2",OrderSide="SELL",StrikePrice=24300,Expiry="11JUL2024",orderType="Market",productType="NRML",Quantity=25,OptionType="PE",timeInForce="DAY"
Temp1=getGeeks(ticker="NIFTY",Expiry="11JUL2024",GeekType="Delta",StrikePrice="SpotATM",Exchange="NFO",OptionType="CE")
Temp2=Temp1-0.11
Leg="A",Counter="3",OrderSide="BUY",Delta=Temp2,Expiry="11JUL2024",orderType="LimitThanMarket",Sequence=10,Steps=0.05,productType="NRML",Quantity=25,OptionType="CE",timeInForce="DAY"
Temp3=Temp1+0.11
Leg="A",Counter="4",OrderSide="BUY",Delta=Temp3,Expiry="11JUL2024",orderType="LimitThanMarket",Sequence=10,Steps=0.05,productType="NRML",Quantity=25,OptionType="PE",timeInForce="DAY"
"""

EntryLeg = compile_user_input(user_input)
print(result)

#-----------------------------Executing Entry Leg------------------------------------#
EntryLeg = process_orders(EntryLeg, User_Broker_Connection, username, BrokerName)

