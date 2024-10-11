# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 13:51:52 2024

@author: Home
"""
##Dhoni
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

instrument_url="https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
response=urllib.request.urlopen(instrument_url)
instrument_List=json.loads(response.read())

MarketAPI="d6f4261dd80f4a0e8adc80"
MarketSecret="Rhdp825@bU"
source="WEBAPI"

MarketConnection=XTSConnect(MarketAPI, MarketSecret, source)
response = MarketConnection.marketdata_login()
AngelMarketConnect=AngelConnection("931649")

#--------Instrument Details--------#
ScriptName="SENSEX"
exchange="BSE"
TokenID=get_instrument_id (ScriptName,instrument_List,expiryDate="",strikePrice="",exchange=exchange,OptionType="")
Spot=AngelMarketConnect[1].ltpData(exchange,ScriptName,TokenID)["data"]['ltp']
#----------------Caluclating Synthetic Futures and associated ATM's------------------------#
expiryDate="12JUL2024"
NFOExchange="BFO"
SpotATM=get_atm__strikePrice (ScriptName,instrument_List,expiryDate,Spot,NFOExchange,"CE",RoundUp="True")
Spot_ATM_CE_Token=get_instrument_id (ScriptName,instrument_List,expiryDate=expiryDate,strikePrice=ScriptATM,exchange=NFOExchange,OptionType="CE")
Spot_ATM_PE_Token=get_instrument_id (ScriptName,instrument_List,expiryDate=expiryDate,strikePrice=ScriptATM,exchange=NFOExchange,OptionType="PE")
Spot_ATM_CE_LTP=AngelMarketConnect[1].ltpData(NFOExchange,ScriptName,Spot_ATM_CE_Token)["data"]['ltp']
Spot_ATM_PE_LTP=AngelMarketConnect[1].ltpData(NFOExchange,ScriptName,Spot_ATM_PE_Token)["data"]['ltp']
Spot_SynthFut=Spot+Spot_ATM_CE_LTP-Spot_ATM_PE_LTP
SynthATM=get_atm__strikePrice(ScriptName,instrument_List,expiryDate,Spot_SynthFut,NFOExchange,"CE",RoundUp="True")

Synth_ATM_CE_Token=get_instrument_id (ScriptName,instrument_List,expiryDate=expiryDate,strikePrice=SynthATM,exchange=NFOExchange,OptionType="CE")
Synth_ATM_PE_Token=get_instrument_id (ScriptName,instrument_List,expiryDate=expiryDate,strikePrice=SynthATM,exchange=NFOExchange,OptionType="PE")
Synth_ATM_CE_LTP=AngelMarketConnect[1].ltpData(NFOExchange,ScriptName,Synth_ATM_CE_Token)["data"]['ltp']
Synth_ATM_PE_LTP=AngelMarketConnect[1].ltpData(NFOExchange,ScriptName,Synth_ATM_PE_Token)["data"]['ltp']

if abs(SynthFut_ATM_PE-SynthFut_ATM_CE)>abs(ScriptLTP_ATM_CE-ScriptLTP_ATM_PE):
    BestATM=ScriptATM
else:
    BestATM=ScriptATM_SynthFut
#-----------------------get ATM and target geeks------------------------#
greekParam={"name":ScriptName,
            "expirydate":expiryDate}
geekDF=pd.DataFrame(AngelMarketConnect[1].optionGreek(greekParam)["data"])
ATMGeek=geekDF[(geekDF["strikePrice"].astype(float)==float(BestATM)/100)]
ATMDeltaCE=ATMGeek[(ATMGeek["optionType"]=="CE")]["delta"].values[0]
ATMDeltaPE=ATMGeek[(ATMGeek["optionType"]=="PE")]["delta"].values[0]
DeltaHedgeFactor=0.11
TargetDetlaCE=float(ATMDeltaCE)-DeltaHedgeFactor
TargetDetlaPE=float(ATMDeltaPE)+DeltaHedgeFactor

#---------------------------------------------------------------------------

#-------------------Get target geek strike price and option preimums-------#
geekDF["CE_Diff"]=geekDF["delta"].astype(float)-TargetDetlaCE
geekDF["PE_Diff"]=geekDF["delta"].astype(float)-TargetDetlaPE

TargetDetlaCEStrPrice=geekDF[(geekDF["optionType"]=="CE") & (geekDF["CE_Diff"].abs()==geekDF["CE_Diff"].abs().min())]["strikePrice"].astype(float).values[0]
TargetDetlaPEStrPrice=geekDF[(geekDF["optionType"]=="PE") & (geekDF["PE_Diff"].abs()==geekDF["PE_Diff"].abs().min())]["strikePrice"].astype(float).values[0]

TargetDetlaCEStrPriceATM=get_atm__strikePrice(ScriptName,instrument_List,expiryDate,TargetDetlaCEStrPrice,NFOExchange,"CE",RoundUp="False")
TargetDetlaPEStrPriceATM=get_atm__strikePrice(ScriptName,instrument_List,expiryDate,TargetDetlaPEStrPrice,NFOExchange,"PE",RoundUp="False")

TargetDetlaCEStrPrice_TokenID=get_instrument_id (ScriptName,instrument_List,expiryDate=expiryDate,strikePrice=TargetDetlaCEStrPriceATM,exchange="NFO",OptionType="CE")
TargetDetlaPEStrPrice_TokenID=get_instrument_id (ScriptName,instrument_List,expiryDate=expiryDate,strikePrice=TargetDetlaPEStrPriceATM,exchange="NFO",OptionType="PE")

TargetDetlaCELTP=AngelMarketConnect[1].ltpData(NFOExchange,ScriptName,TargetDetlaCEStrPrice_TokenID)["data"]['ltp']
TargetDetlaPELTP=AngelMarketConnect[1].ltpData(NFOExchange,ScriptName,TargetDetlaPEStrPrice_TokenID)["data"]['ltp']

#----------------------------------------------------------------------------#

NetPremium=(ScriptLTP_ATM_CE+ScriptLTP_ATM_PE)-(TargetDetlaCELTP+TargetDetlaPELTP)
MaxLossCE=(float(TargetDetlaCEStrPriceATM)-float(ScriptATM))/100-NetPremium
MaxLossPE=(float(ScriptATM)-float(TargetDetlaPEStrPriceATM))/100-NetPremium

#------------------------------------------------------------------------------------------------#
#---------Place hedge order----------------------------------------------------------------------#
BrokerName= "Wisdom Capital"
api_key="865e5797741bc21838e722"
api_secretKey="Luur308@gK"
username="WD3868"

MarketAPI="d6f4261dd80f4a0e8adc80"
MarketSecret="Rhdp825@bU"
source="WEBAPI"

MarketConnection=XTSConnect(MarketAPI, MarketSecret, source)
response = MarketConnection.marketdata_login()
print("MarketData Login: ", response)

User_Broker_Connection=connect_and_create_websocket(BrokerName,api_key,api_secretKey,user
                                                    name, pwd="none", authenticator="none")
response = User_Broker_Connection.interactive_login()
print(response)


token_list=[
            {"exchangeSegment":2,"exchangeInstrumentID":"55220"},
            {"exchangeSegment":2,"exchangeInstrumentID":"55225"},
            {"exchangeSegment":2,"exchangeInstrumentID":"55234"},
            {"exchangeSegment":2,"exchangeInstrumentID":"55215"},
            ]
"""Send Subscription Request"""
Subs_response = MarketConnection.send_subscription(
    Instruments=token_list,
    xtsMessageCode=1502)
print('Subscribe :', response)

data = {
    'orderSide': ['BUY','BUY',"Sell","Sell"],
    'exchangeSegment': ['NFO', 'NFO', 'NFO','NFO'],
    'exchangeInstrumentID': ["55220","55225","55234","55215"],
    'productType': ['NRML','NRML','NRML','NRML'],
    'timeInForce': ['DAY','DAY','DAY','DAY'],
    'disclosedQuantity': [0,0,0,0],
    'orderType': ['LIMIT','LIMIT','LIMIT','LIMIT'],
    'StartPrice':[0,0,0,0],
    'EndPrice':[0,0,0,0],
    'Quantity':[15,15,15,15],
    'Sequence':[10,10,10,10],
    'Steps':[0.05,0.05,0.05,0.05]
}
OrderLeg=pd.DataFrame(data)


for i in range(0,(len(token_list))):
    Subscription=Subs_response['result']['listQuotes'][i]
    parsed_data = json.loads(Subscription)
    bids = pd.DataFrame(parsed_data['Bids'])
    asks = pd.DataFrame(parsed_data['Asks'])
    startPrice=bids["Price"].max()    
    EndPrice=asks["Price"].max()
    if OrderLeg["orderSide"][i]=="BUY":
        OrderLeg["StartPrice"][i]=startPrice
        OrderLeg["EndPrice"][i]=EndPrice
    else:
       OrderLeg["StartPrice"][i]=EndPrice
       OrderLeg["EndPrice"][i]=startPrice
       
def SmartOrder(row):
    exchangeSegment = row['exchangeSegment']
    exchangeInstrumentID = row['exchangeInstrumentID']
    productType = row['productType']
    StartPrice = row['StartPrice']
    timeInForce = row['timeInForce']
    EndPrice = row['EndPrice']
    Sequence = row['Sequence']
    Steps = row['Steps']
    orderSide = row['orderSide']
    Quantity = row['Quantity']
    
    Status = "Start"
    t = 0
    
    while Status != "Complete" and t <= Sequence:
        if orderSide == "BUY":
            StartPrice = max(StartPrice + t * Steps, EndPrice)
        else:
            StartPrice = min(StartPrice - t * Steps, EndPrice)
        
        if Status == "Start":
            response = User_Broker_Connection.place_order(
                exchangeSegment=exchangeSegment,
                exchangeInstrumentID=exchangeInstrumentID,
                productType=productType,
                orderType="LIMIT",
                orderSide=orderSide,
                timeInForce=timeInForce,
                disclosedQuantity=0,
                orderQuantity=Quantity,
                limitPrice=StartPrice,
                stopPrice=0,
                orderUniqueIdentifier="454845",
                clientID=username
            )
            
            # extracting the order id from response
            if response['type'] != 'error':
                OrderID = response['result']['AppOrderID']
                response = pd.DataFrame(User_Broker_Connection.get_order_history(appOrderID=OrderID, clientID=username)["result"])
                Status = response["OrderStatus"].iloc[-1]
        
        if Status == "New" or Status == "Replaced":
            response = User_Broker_Connection.modify_order(
                appOrderID=OrderID,
                modifiedProductType=productType,
                modifiedOrderType="LIMIT",
                modifiedOrderQuantity=Quantity,
                modifiedDisclosedQuantity=0,
                modifiedLimitPrice=50,
                modifiedStopPrice=0,
                modifiedTimeInForce=timeInForce,
                orderUniqueIdentifier="454845",
                clientID=username
            )
            response = pd.DataFrame(User_Broker_Connection.get_order_history(appOrderID=OrderID, clientID=username)["result"])
            Status = response["OrderStatus"].iloc[-1]
        
        t += 1
    
    return Status 
            # Apply SmartOrder function to each row
OrderLeg['OrderStatus'] = OrderLeg.apply(SmartOrder, axis=1)

