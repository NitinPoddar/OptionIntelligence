# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 13:56:44 2024

@author: Nitin
"""

from SmartApi import SmartConnect
from SmartApi import smartWebSocketV2

import os
import urllib
import json
import pandas as pd
import datetime as dt
from datetime import date
from dateutil.relativedelta import relativedelta, TH

instrument_url="https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
response=urllib.request.urlopen(instrument_url)
instrument_List=json.loads(response.read())
tickers={"INFY","HDFCBANK","ICICIBANK","LT","ITC","RELIANCE"}


key_path = r"C:\Users\Home\Angel Trading"
os.chdir(key_path)
key_secret = open("Key.txt", "r").read().split()


apikey = key_secret[0]
apikey = "h8UJWcxl"
api_secretKey = key_secret[1]
username = key_secret[2]
pwd = key_secret[3]
TOTPKey = key_secret[4]
#uthenticator=TOTP(TOTPKey).now()
Authenticator="357315"
obj = SmartConnect(api_key=apikey)
data = obj.generateSession(username, pwd, Authenticator)
feed_token=obj.getfeedToken()
token="nse_cm|1594&nse_cm|1330"
task="mw"

sws = SmartWebSocketV2(data["data"]["jwtToken"], apikey, username, feed_token)


def token_lookup(ticker,instrument_list,exchange="NSE"):
  for instrument in instrument_list:
      if instrument['name']==ticker and instrument["exch_seg"]==exchange and instrument["symbol"].split('-')[-1]=="EQ":
          return instrument['token']
      
        
def stream_list(list_stocks,instrument_list,exchange="nse_cm"):
    return_string=''
    for count,ticker in enumerate(list_stocks):
        if count!=0:
            return_string+="&"+exchange+"|"+token_lookup(ticker,instrument_list)
        else:
            return_string+=exchange+"|"+token_lookup(ticker,instrument_list)
    return return_string

correlation_id="stream1"
action=1
mode=3        
token_list=[{"exchangeType":1,"tokens":["26009"]}]

def on_data(wsapp, message):
    print("Ticks: {}".format(message))

def on_open(wsapp):
     print("On Open")
     sws.subscribe(correlation_id,mode,token_list)

    
def on_error(wsapp,error):
     print(error)
     
def on_close(wsapp):
    print("On close")

   
 
sws.on_open=on_open
sws.on_data=on_data
sws.on_error=on_error
    
sws.connect()
 
