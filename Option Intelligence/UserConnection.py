# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 21:26:58 2024

@author: Home
"""

from Connect import XTSConnect
from InteractiveSocketClient import OrderSocket_io
import pandas as pd
from SmartApi import SmartConnect
import pyotp
from logzero import logger
from SmartApi import SmartWebSocket
import os
import json
import datetime
import pytz
import tzlocal
def connect_and_create_websocket(BrokerName,api_key,api_secretKey,username, pwd="none", authenticator="none"):
    if BrokerName=="Wisdom Capital":
        ss = XTSConnect(api_key, api_secretKey, "WEBAPI")
        return ss
    elif BrokerName=="Angel Broking":
        obj = SmartConnect(api_key=api_key)
        data = obj.generateSession(username, pwd, authenticator)
        feed_token = obj.getfeedToken()
        ss = SmartWebSocket(feed_token, username)
        return data,ss
    
#---Place order is working can get token from instrument list downloaded from angel broking
def get_indexExchange(ticker):
    df_data=pd.DataFrame(instrument_List,columns=["token","symbol","name","expiry","strike","lotsize","exch_seg","tick_size","instrumenttype"])
    filtered_df = df_data[(df_data['expiry']=='') & (df_data['name']==ticker) ]
    return filtered_df["exch_seg"].values[0]

def get_indexToken(ticker):
    df_data=pd.DataFrame(instrument_List,columns=["token","symbol","name","expiry","strike","lotsize","exch_seg","tick_size","instrumenttype"])
    filtered_df = df_data[(df_data['expiry']=='') & (df_data['name']==ticker) ]
    return filtered_df["token"].values[0]

def get_OptionExchange(ticker):
    df_data=pd.DataFrame(instrument_List,columns=["token","symbol","name","expiry","strike","lotsize","exch_seg","tick_size","instrumenttype"])
    filtered_df = df_data[(df_data['expiry']!='') & (df_data['name']==ticker) ]
    return filtered_df["exch_seg"].values[0]


def get_lotSize(ticker):
    df_data=pd.DataFrame(instrument_List,columns=["token","symbol","name","expiry","strike","lotsize","exch_seg","tick_size","instrumenttype"])
    filtered_df = df_data[(df_data['expiry']!='') & (df_data['name']==ticker) ]
    return filtered_df["lotsize"].values[0]


def LegDetails(ticker,LegName):
    TokenID=get_indexToken(ticker)
    IndexExchange=get_indexExchange(ticker)
    Spot=AngelMarketConnect[1].ltpData(IndexExchange,ticker,TokenID)["data"]['ltp']
    data = [{
        'Leg': LegName,
        'Script':ticker,
        'IndexExchange':IndexExchange,
        'OptionExchange':get_OptionExchange(ticker),
        'lotsize': get_lotSize(ticker),
        'Spot': Spot
        }]
    return pd.DataFrame(data)

def getGeeks(ticker,Expiry,GeekType,StrikePrice,OptionType):
    
    greekParam={"name":ticker,
                "expirydate":Expiry}
    geekDF=pd.DataFrame(AngelMarketConnect[1].optionGreek(greekParam)["data"])
    TokenID=get_indexToken(ticker)
    IndexExchange=get_indexExchange(ticker)
    LTP=AngelMarketConnect[1].ltpData(IndexExchange,ticker,TokenID)["data"]['ltp']
    
    if StrikePrice=="SpotATM":
        ATM=ATMSpot(ticker,Expiry,LTP,Exchange)['strike'].values[0]
        ATMGeek=geekDF[(geekDF["strikePrice"].astype(float)==float(ATM)/100)]
        
    elif StrikePrice=="SythATM":
        ATM=ATMSynth(ticker,instrument_List,Expiry,LTP,Exchange,AngelMarketConnect)['strike'].values[0]
        ATMGeek=geekDF[(geekDF["strikePrice"].astype(float)==float(ATM)/100)]
    else:
        ATMGeek=geekDF[(geekDF["strikePrice"].astype(float)==StrikePrice)]
    
    Geek=ATMGeek[(ATMGeek["optionType"]==OptionType)][GeekType].values[0]
    
    return float(Geek)

def getInstrumentIdFromGeek(ticker,Expiry,AngelMarketConnect,GeekType,GeekValue,instrumentlist,Exchange,OptionType):
    greekParam={"name":ticker,
                "expirydate":Expiry}
    geekDF=pd.DataFrame(AngelMarketConnect[1].optionGreek(greekParam)["data"])
    geekDF["Temp"]=geekDF[GeekType].astype(float)-GeekValue
    geekDF["Temp"]=geekDF["Temp"].abs()
    geekDF=geekDF[(geekDF["Temp"]==geekDF["Temp"].min())]
    geekDF["strikePrice"]=geekDF["strikePrice"].astype(float)
    StrikePrice=geekDF["strikePrice"].values[0]
    ATM=ATMSpot(ticker,instrumentlist,Expiry,StrikePrice,Exchange)
    InstrumentID=ATM[(ATM['OptionType']==OptionType)]['token'].values[0]
    return InstrumentID

def getOTMStrike(ticker,Expiry,Premium,OptionType):
    
    TokenID=get_indexToken(ticker)
    IndexExchange=get_indexExchange(ticker)
    OptionExchange=get_OptionExchange(ticker)

    LTP=AngelMarketConnect[1].ltpData(IndexExchange,ticker,TokenID)["data"]['ltp']
    df_data=pd.DataFrame(instrument_List,columns=["token","symbol","name","expiry","strike","lotsize","exch_seg","tick_size"])
    filtered_df = df_data[(df_data['name']==ticker) & (df_data['expiry']==Expiry)]
    filtered_df.loc[:, 'strike'] = pd.to_numeric(filtered_df['strike'], errors='coerce')
    filtered_df.loc[:, 'Optiontype']=df_data['symbol'].str[-2:]
    LTP=LTP*100
    if OptionType=="CE":
        filtered_df = filtered_df[(filtered_df['strike']>LTP) & (filtered_df['Optiontype']==OptionType)].sort_values(by=['strike']) 
    elif OptionType=="PE":
        filtered_df = filtered_df[(filtered_df['strike']<LTP)& (filtered_df['Optiontype']==OptionType)].sort_values(by=['strike'],ascending=False)
    else:
        print("Incorret Option Type---choose from 'PE' or 'CE'")
    #def process_row(row):
     #   return AngelMarketConnect[1].ltpData(OptionExchange,ticker,row['token'])["data"]['ltp']
    
    Curr_DiffFomTrgt=abs(AngelMarketConnect[1].ltpData(OptionExchange,ticker,filtered_df['token'].values[0])["data"]['ltp']-Premium)
    Prev_DiffFomTrgt=Curr_DiffFomTrgt
    c=1
    while Curr_DiffFomTrgt<=Prev_DiffFomTrgt:
        Curr_Prem=AngelMarketConnect[1].ltpData(OptionExchange,ticker,filtered_df['token'].values[c])["data"]['ltp'] 
        Curr_DiffFomTrgt=abs(Curr_Prem-Premium)
        if Curr_DiffFomTrgt<Prev_DiffFomTrgt:
            Prev_DiffFomTrgt=Curr_DiffFomTrgt
            c=c+1
        else:
            FinalStrike=filtered_df['strike'].values[c-1]
           
    return FinalStrike  

def get_instrument_id (ticker,instrumentlist,expiryDate,strikePrice,Delta,Gamma,Vega,exchange,OptionType):
    df_data=pd.DataFrame(instrumentlist,columns=["token","symbol","name","expiry","strike","lotsize","exch_seg","tick_size","instrumenttype"])
    if exchange=="NFO" or exchange=="BFO":
        filtered_df = df_data[(df_data['exch_seg'] == exchange) & (df_data['name']==ticker) & (df_data['expiry']==expiryDate) & (df_data['strike']==strikePrice) & (df_data['symbol'].str[-2:]==OptionType)]

    elif exchange=="NSE" or exchange=="BSE" :
            filtered_df = df_data[(df_data['exch_seg'] == exchange) & (df_data['name']==ticker) & (df_data['symbol'].str[-2:]=="EQ")]
            if filtered_df.empty:
                filtered_df = df_data[(df_data['exch_seg'] == exchange) & (df_data['name'] == ticker) & (df_data['instrumenttype'] == "AMXIDX")]
    return filtered_df['token'].values[0]
       
def get_instrument_details (ticker,instrumentlist):
    for instrument in instrument_List:
        if instrument['token']==ticker:
            return instrument['symbol'],instrument['name'],instrument["exch_seg"],instrument["strike"],instrument["expiry"]

def ATMSpot(ticker,Expiry,LTP):    
    df_data=pd.DataFrame(instrument_List,columns=["token","symbol","name","expiry","strike","lotsize","exch_seg","tick_size"])
    filtered_df = df_data[(df_data['exch_seg'] == Exchange) & (df_data['name']==ticker) & (df_data['expiry']==Expiry)]
    filtered_df.loc[:, 'strike'] = pd.to_numeric(filtered_df['strike'], errors='coerce')
    LTP=LTP*100
    filtered_df.loc[:, 'strike_Adj_LTP'] = (float(LTP)- filtered_df.loc[:, 'strike'])
    filtered_df.loc[:, 'strike_Adj_LTP'] = filtered_df.loc[:, 'strike_Adj_LTP'].abs()
    ATM=filtered_df[filtered_df["strike_Adj_LTP"]==filtered_df["strike_Adj_LTP"].min()]
    ATM.loc[:, 'OptionType'] = ATM.loc[:,'symbol'].str[-2:]
    return ATM

def ATMSynth(ticker,Expiry,LTP):
    df_data=pd.DataFrame(instrument_List,columns=["token","symbol","name","expiry","strike","lotsize","exch_seg","tick_size"])
    filtered_df = df_data[(df_data['exch_seg'] == Exchange) & (df_data['name']==ticker) & (df_data['expiry']==Expiry)]
    filtered_df.loc[:, 'strike'] = pd.to_numeric(filtered_df['strike'], errors='coerce')
    LTP=LTP*100
    filtered_df.loc[:, 'strike_Adj_LTP'] = (float(LTP)- filtered_df.loc[:, 'strike'])
    filtered_df.loc[:, 'strike_Adj_LTP'] = filtered_df.loc[:, 'strike_Adj_LTP'].abs()
    ATM=filtered_df[filtered_df["strike_Adj_LTP"]==filtered_df["strike_Adj_LTP"].min()]
    ATMCEToken=ATM[(df_data['symbol'].str[-2:]=="CE")]["token"].values[0]
    ATMPEToken=ATM[(df_data['symbol'].str[-2:]=="PE")]["token"].values[0]
    Spot_ATM_CE_LTP=AngelMarketConnect[1].ltpData(Exchange,ticker,ATMCEToken)["data"]['ltp']
    Spot_ATM_PE_LTP=AngelMarketConnect[1].ltpData(Exchange,ticker,ATMPEToken)["data"]['ltp']
    Synth= (LTP/100+Spot_ATM_CE_LTP-Spot_ATM_PE_LTP)*100
    filtered_df['strike_Adj_Synth'] =  (Synth-filtered_df.loc[:, 'strike'])
    filtered_df.loc[:, 'strike_Adj_Synth'] = filtered_df.loc[:, 'strike_Adj_Synth'].abs()
    SynthATM=filtered_df[filtered_df["strike_Adj_Synth"]==filtered_df["strike_Adj_Synth"].min()]
    SynthATM['OptionType']=SynthATM['symbol'].str[-2:]
    return SynthATM

def getExchangeSegmentNo(Exchange):    
    if Exchange=="NSECM":
        exchangeSegment=1
    elif Exchange=="NSEFO":
        exchangeSegment=2
    elif Exchange=="NSECD":
        exchangeSegment=3
    elif Exchange=="MCXFO":
        exchangeSegment=4
    elif Exchange=="BSECM":
        exchangeSegment=5
    elif Exchange=="BSEFO":
        exchangeSegment=12
    return exchangeSegment

def Option(Leg,OrderSide,LimitPrice,StrikePrice,delta,vega,gamma,impliedVolatility,Expiry,orderType,productType,Sequence,Steps,Quantity,OptionType,timeInForce):
    Exchange=Leg['OptionExchange'].values[0]
    ticker=Leg['Script'].values[0]
    LTP=Leg['Spot'].values[0]
    if delta==0 and vega==0 and gamma==0 and impliedVolatility==0:
        if StrikePrice=="SpotATM":
            ATM=ATMSpot(ticker,Expiry,LTP)
            InstrumentID=ATM[(ATM['OptionType']==OptionType)]['token'].values[0]
        elif StrikePrice=="SynthATM":
            ATM=ATMSynth(ticker,Expiry,LTP)
            InstrumentID=ATM[(ATM['OptionType']==OptionType)]['token'].values[0] 
        else:
           ATM=ATMSpot(ticker,Expiry,StrikePrice)
           InstrumentID=ATM[(ATM['OptionType']==OptionType)]['token'].values[0]
    else:
        if abs(delta)>0:
            InstrumentID=getInstrumentIdFromGeek(ticker, Expiry, "delta", delta, Exchange, OptionType)
        elif abs(gamma)>0:
            InstrumentID=getInstrumentIdFromGeek(ticker, Expiry,"gamma", gamma,Exchange, OptionType)
        elif abs(vega)>0:
            InstrumentID=getInstrumentIdFromGeek(ticker, Expiry, "vega", vega, instrumentlist, Exchange, OptionType)
        elif abs(impliedVolatility)>0:
            InstrumentID=getInstrumentIdFromGeek(ticker, Expiry, "impliedVolatility", impliedVolatility, OptionType)
    if Exchange=="NSE":
        exchange="NSECM"
        exchangeSegment=1
    elif Exchange=="NFO":
        exchange="NSEFO"
        exchangeSegment=2
    elif Exchange=="CDS":
        exchange="NSECD"
        exchangeSegment=3
    elif Exchange=="MCX":
        exchange="MCXFO"
        exchangeSegment=4
    elif Exchange=="BSE":
        exchange="BSECM"
        exchangeSegment=5
    elif Exchange=="BFO":
        exchange="BSEFO"
        exchangeSegment=12
      
    
    if orderType=="LimitThanMarket":
        token_list=[{"exchangeSegment":exchangeSegment,"exchangeInstrumentID":InstrumentID}]
        """Send Subscription Request"""
        Subs_response = MarketConnection.send_unsubscription(
            Instruments=token_list,
            xtsMessageCode=1502)
        Subs_response = MarketConnection.send_subscription(
            Instruments=token_list,
            xtsMessageCode=1502)
        Subscription=Subs_response['result']['listQuotes'][0]
        parsed_data =json.loads(Subscription)
        bids = pd.DataFrame(parsed_data['Bids'])
        asks = pd.DataFrame(parsed_data['Asks'])
        StartPrice=bids["Price"].max()    
        EndPrice=asks["Price"].max()
    else:
        StartPrice=0    
        EndPrice=0
    Leg['orderSide']=OrderSide
    Leg["exchangeSegment"]=exchange
    Leg["orderType"]=orderType
    Leg["exchangeInstrumentID"]=InstrumentID
    Leg['StartPrice'] = StartPrice
    Leg['EndPrice'] = EndPrice
    Leg['productType']=productType
    Leg['timeInForce'] = timeInForce
    Leg['Sequence'] = Sequence
    Leg['Steps'] = Steps
    Leg['Quantity'] = Quantity
    Leg['LimitPrice'] = LimitPrice
    return Leg

    #--------rearrange in best was you want---------#
            
def get_atm__strikePrice (ticker,instrumentlist,expiryDate,LTP,exchange,OptionType,RoundUp,Type):
    df_data=pd.DataFrame(instrumentlist,columns=["token","symbol","name","expiry","strike","lotsize","exch_seg","tick_size"])
    filtered_df = df_data[(df_data['exch_seg'] == exchange) & (df_data['name']==ticker) & (df_data['expiry']==expiryDate) & (df_data['symbol'].str[-2:]==OptionType)]
    #cols_to_convert = ['strike', 'lotsize', 'tick_size']
    #filtered_df[cols_to_convert] = filtered_df[cols_to_convert].astype(float)
    if RoundUp=="True":
        filtered_df['strike_Adj_LTP'] =  (LTP*100-filtered_df['strike'].astype(float)).abs()
        ATM=filtered_df[filtered_df["strike_Adj_LTP"]==filtered_df["strike_Adj_LTP"].min()]
    elif OptionType=="PE":
        filtered_df['strike_Adj_LTP'] = filtered_df['strike'].astype(float)- LTP*100
        Atm_filtered_df = filtered_df[(filtered_df['strike_Adj_LTP'] >= 0)]
        ATM=Atm_filtered_df[Atm_filtered_df["strike_Adj_LTP"]==Atm_filtered_df["strike_Adj_LTP"].min()]
    else :
        filtered_df['strike_Adj_LTP'] =  LTP*100-filtered_df['strike'].astype(float)
        Atm_filtered_df = filtered_df[(filtered_df['strike_Adj_LTP'] >= 0)]
        ATM=Atm_filtered_df[Atm_filtered_df["strike_Adj_LTP"]==Atm_filtered_df["strike_Adj_LTP"].min()]
    
    return ATM['strike'].values[0]


def SmartOrder(row,User_Broker_Connection,username,Broker):
    
    exchangeSegment = row['exchangeSegment']
    exchangeInstrumentID = int(row['exchangeInstrumentID'])
    productType = row['productType']
    StartPrice = float(row['StartPrice'])-1
    timeInForce = row['timeInForce']
    EndPrice = float(row['EndPrice'])
    Sequence = int(row['Sequence'])
    Steps = float(row['Steps'])
    LimitPrice=float(row['LimitPrice'])
    orderSide = row['orderSide']
    Quantity = int(row['Quantity'])
    orderType = row['orderType']
    if Broker=="Wisdom Capital":
        if orderType=="LIMIT":
            response = User_Broker_Connection.place_order(
                exchangeSegment=exchangeSegment,
                exchangeInstrumentID=exchangeInstrumentID,
                productType=productType,
                orderType="LIMIT",
                orderSide=orderSide,
                timeInForce=timeInForce,
                disclosedQuantity=0,
                orderQuantity=Quantity,
                limitPrice=LimitPrice,
                stopPrice=0,
                orderUniqueIdentifier="454845",
                clientID=username
            )
            # extracting the order id from response
            if response['type'] != 'error':
                OrderID = response['result']['AppOrderID']
                response = pd.DataFrame(User_Broker_Connection.get_order_history(appOrderID=OrderID, clientID=username)["result"])
                Status = response["OrderStatus"].iloc[-1]
        elif orderType=="MARKET":
                response = User_Broker_Connection.place_order(
                    exchangeSegment=exchangeSegment,
                    exchangeInstrumentID=exchangeInstrumentID,
                    productType=productType,
                    orderType="MARKET",
                    orderSide=orderSide,
                    timeInForce=timeInForce,
                    disclosedQuantity=0,
                    orderQuantity=Quantity,
                    limitPrice=0,
                    stopPrice=0,
                    orderUniqueIdentifier="454845",
                    clientID=username
                )
                # extracting the order id from response
                if response['type'] != 'error':
                    OrderID = response['result']['AppOrderID']
                    response = pd.DataFrame(User_Broker_Connection.get_order_history(appOrderID=OrderID, clientID=username)["result"])
                    Status = response["OrderStatus"].iloc[-1]
        else:
            Status = "Start"
            t = 0
            
            while Status not in ["Filled", "Complete"] and t <= Sequence:
                if orderSide == "BUY":
                    OrderPrice = StartPrice
                else:
                    OrderPrice = EndPrice
                
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
                        limitPrice=OrderPrice,
                        stopPrice=0,
                        orderUniqueIdentifier="454845",
                        clientID=username
                    )
                    if response['type'] != 'error':
                        OrderID = response['result']['AppOrderID']
                        response = pd.DataFrame(User_Broker_Connection.get_order_history(appOrderID=OrderID, clientID=username)["result"])
                        Status = response["OrderStatus"].iloc[-1]
                        print(Status)  
                if orderSide == "BUY":
                    StartPrice = min(float(StartPrice) + float(Steps), float(EndPrice))
                    OrderPrice=StartPrice
                else:
                    EndPrice=EndPrice - Steps
                    OrderPrice = max(EndPrice, StartPrice)
                print(Status)
                print(StartPrice)
                print(Steps)
                print(EndPrice)
                if Status == "New" or Status == "Replaced":
                    response = User_Broker_Connection.modify_order(
                        appOrderID=OrderID,
                        modifiedProductType=productType,
                        modifiedOrderType="LIMIT",
                        modifiedOrderQuantity=Quantity,
                        modifiedDisclosedQuantity=0,
                        modifiedLimitPrice=OrderPrice,
                        modifiedStopPrice=0,
                        modifiedTimeInForce=timeInForce,
                        orderUniqueIdentifier="454845",
                        clientID=username
                    )
                    #time.sleep(1)
                    response = pd.DataFrame(User_Broker_Connection.get_order_history(appOrderID=OrderID, clientID=username)["result"])
                    Status = response["OrderStatus"].iloc[-1] 
                t=t+1    
            if Status!="Filled" or Status!="Complete":
                response = User_Broker_Connection.modify_order(
                        appOrderID=OrderID,
                        modifiedProductType=productType,
                        modifiedOrderType="MARKET",
                        modifiedOrderQuantity=Quantity,
                        modifiedDisclosedQuantity=0,
                        modifiedLimitPrice=0,
                        modifiedStopPrice=0,
                        modifiedTimeInForce=timeInForce,
                        orderUniqueIdentifier="454845",
                        clientID=username 
                        )
                #time.sleep(1)
            response = pd.DataFrame(User_Broker_Connection.get_order_history(appOrderID=OrderID, clientID=username)["result"])
            Status = response["OrderStatus"].iloc[-1]
            ExecPrice=response["OrderAverageTradedPrice"].iloc[-1]
    return Status,OrderID,ExecPrice 

def OhlcResponseToDF(OhlcResponse):
    records = OhlcResponse.split(',')
    data_list = []
    for record in records:
        fields = record.split('|')
        data_dict = {
            'timestamp': int(fields[0]),
            'open': float(fields[1]),
            'high': float(fields[2]),
            'low': float(fields[3]),
            'close': float(fields[4]),
            'volume': int(fields[5]),
            'unknown': int(fields[6])
        }
        data_list.append(data_dict)
    
    # Get the local time zone
    local_tz = tzlocal.get_localzone()
    
    # Convert each timestamp to the local time zone
    for entry in data_list:
        dt_object = datetime.datetime.fromtimestamp(entry['timestamp'], pytz.utc)
        entry['local_time'] = dt_object
    
    
    return data_list

def candle(exchangeInstrumentID,startTime,endTime,tick):
    response = MarketConnection.get_ohlc(
         exchangeSegment="NSEFO",
         exchangeInstrumentID=exchangeInstrumentID,
         startTime=startTime,
         endTime=endTime,
         compressionValue=tick*60)
    return pd.DataFrame(OhlcResponseToDF(response['result']['dataReponse']))



def process_orders(df, User_Broker_Connection, username, Broker):
    results = []    
    for index, row in df.iterrows():
        exchangeSegment = row['exchangeSegment']
        exchangeInstrumentID = row['exchangeInstrumentID']
        productType = row['productType']
        StartPrice = row['StartPrice']
        timeInForce = row['timeInForce']
        EndPrice = row['EndPrice']
        Sequence = row['Sequence']
        Steps = row['Steps']
        LimitPrice = row['LimitPrice']
        orderSide = row['orderSide']
        Quantity = row['Quantity']
        orderType = row['orderType']
        
        # Call SmartOrder function
        status, orderID, ExecPrice = SmartOrder(row, User_Broker_Connection, username, Broker)
        
        # Store results or process further as needed
        results.append({'Status': status, 'OrderID': orderID,'ExecPrice': ExecPrice})
    
    return results

       
#-----------------------get ATM and target geeks------------------------#
