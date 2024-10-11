# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 13:32:09 2024

@author: Nitin
"""
import json


AlgoName="KOHLINIFTY"
Quantity=45
AlgoDetails=

TargetPremium=30
if isTrueOptionPosition(2)and DaystoExpiry=0 and Time>"09:18"':
    print ("success")

#--------Replace with real time loop-----#
GetPosition=User_Broker_Connection.get_position_netwise(clientID=clientID)
#--Enhance algo details table to add positions exist or not---#

#--------------------------------------#
for Algos in AlgoDetails:
    #-----Run Enty---"
    if Trade("Position",Index=0)=="FALSE":
        
        


json_string='["TargetPremium=30 and\r\nisTrueOptionPosition(2)and\r\nDaystoExpiry>0 and\r\nTime>\"09:20\"", "TargetPremium=30 and\r\nisTrueOptionPosition(2)and\r\nDaystoExpiry=0 and\r\nTime>\"09:18\"", "TargetPremium=7 and\r\nDaystoExpiry>0 and\r\nTime>\"09:20\""]'
json_string = '["TargetPremium=30 and\\r\\nisTrueOptionPosition(2)and\\r\\nDaystoExpiry>0 and\\r\\nTime>\\"09:20\\"", "TargetPremium=30 and\\r\\nisTrueOptionPosition(2)and\\r\\nDaystoExpiry=0 and\\r\\nTime>\\"09:18\\"", "TargetPremium=7 and\\r\\nDaystoExpiry>0 and\\r\\nTime>\\"09:20\\""]'

# Parse the JSON string into a Python list
conditions = json.loads(json_string)

# Function to transform each condition string into a valid Python expression
def transform_conditions(conditions):
    transformed = []
    for condition in conditions:
        # Replace the escape sequences and remove unnecessary whitespace
        condition = condition.replace('\\r\\n', ' ').strip()
        transformed.append(condition)
    return transformed

["Premium=30;\r\nTrade(1).position=\"True\";\r\nTime>\"09:30\";\r\nDaysToExpiry>=1", "Premium=30;\r\nTrade(1).position=\"True\";\r\nTime>\"09:30\";\r\nDaysToExpiry>=1"]

# Transform the conditions
python_conditions = transform_conditions(conditions)

# Print the transformed conditions
for cond in python_conditions:
    print(cond)
    
response = User_Broker_Connection.place_order(
    exchangeSegment="NSEFO",
    exchangeInstrumentID=54767,
    productType="NRML",
    orderType='LIMIT',
    orderSide='Sell',
    timeInForce='DAY',
    disclosedQuantity=0,
    orderQuantity=25,
    limitPrice=160,
    stopPrice=0,
    orderUniqueIdentifier="KohliOption1",
    clientID="WD4612")
print("Place Order: ", response)