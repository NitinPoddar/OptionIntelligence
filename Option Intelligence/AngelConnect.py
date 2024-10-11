# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 13:56:44 2024

@author: Nitin
"""

from SmartApi import SmartConnect
from SmartApi import SmartWebSocket

import os

def AngelConnection(Authenticator):
    #key_path = r"C:\Users\Home\Angel Trading"
    #os.chdir(key_path)
    #key_secret = open("Key.txt", "r").read().split()
    #apikey = key_secret[0]
    apikey = "h8UJWcxl"
    api_secretKey = "ded5765c-eb01-bf0c-6101f65137e"
    username = "A218266"
    pwd = "0122"
    #uthenticator=TOTP(TOTPKey).now()
    #Authenticator="985719"
    obj = SmartConnect(api_key=apikey)
    data = obj.generateSession(username, pwd, Authenticator)
    feed_token=obj.getfeedToken()
    ss=SmartWebSocket(feed_token,username)
    return ss,obj,data
