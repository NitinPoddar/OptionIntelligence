#-------Entry Condition-------
# Sell OTM PE of strike price such that premium recieved is close to 30
#Timing of entry on non-expiry day should be 9:20
#Timing of entry on expiry day should be 9:18
# First buy hedge at 75% price of PE sell
#-----calculation steps------#
# 1. Get Time from system time

from datetime import datetime,time,date
from UserConnection import get_indexExchange,connect_and_create_websocket,get_instrument_id,get_atm__strikePrice,getExchangeSegmentNo

Script="NIFTY"
Expiry="31OCT2024"
ScriptToken=get_indexToken(Script)
IndexExchange=get_indexExchange(Script)
OptionExchange=get_OptionExchange(Script)
TargetPEPremium=30
TargetCEPremium=30

OTMStrikePE=getOTMStrike(Script,Expiry,TargetPEPremium,"PE")
LegName='A'
Leg= LegDetails(Script,LegName)       
Quantity=15
Counter="1"
Leg1['Counter']=Counter

OTMEntry(OrderType="Buy",Premium=7,MinPremium=0,AlgoName="Kohli",OptionType="CE",Script="BANKNIFTY",EXPIRY="09OCT2024",CurrentTimeGreater="09:20",CurrentTimeless="14:45")
OTMEntry(OrderType="Sell",Premium=30,MinPremium=7,AlgoName="Kohli",OptionType="CE",Script="BANKNIFTY",EXPIRY="09OCT2024",CurrentTimeGreater="09:20",CurrentTimeless="14:45")
OTMEntry(OrderType="Buy",Premium=7,MinPremium=0,AlgoName="Kohli",OptionType="CE",Script="BANKNIFTY",EXPIRY="09OCT2024",CurrentTimeGreater="09:20",CurrentTimeless="14:45")
OTMEntry(OrderType="Sell",Premium=30,MinPremium=7,AlgoName="Kohli",OptionType="CE",Script="BANKNIFTY",EXPIRY="09OCT2024",CurrentTimeGreater="09:20",CurrentTimeless="14:45")

    
#----------Exit Condition-----1
candle_data=candle(exchangeInstrumentID,startTime,endTime,5)

# Get the relevant values
ema_short = ema(candle_data, 10, 1)
ema_long = ema(candle_data, 20, 1)
close_price = close(candle_data, 1)
supertrend_value = supertrend(candle_data, 14, 2.6, 1)
highest_high_value = HighestHighValue(candle_data, 5, 2)
ema_cross_value = EMACross(candle_data, 10, 20, "high")

# Define thresholds
ltp_threshold = 1.21 * close_price
highest_high_threshold = highest_high_value + 1
ema_cross_threshold = ema_cross_value + 5

# Combine conditions
ExitCondition1 = (
    ema_short > ema_long and
    close_price > supertrend_value and
    LTP > ltp_threshold and
    close_price > highest_high_threshold and
    close_price > ema_cross_threshold
)

#----------Exit Condition2 ------#
ExitCondition2=(
    DaystoExpiry(Expiry)>0 and
    EntryTimeGreater(3) and
    LTP>2.22*IV 
    )
#----------Exit Condition3 ------#
ExitCondition3=(
    EntryTimeGreater(3) and
    LTP<.76*EntryPremium 
    )
#----------Exit Condition4 ------#
ExitCondition4=(
    DaystoExpiry(Expiry)==0 and
    EntryTimeGreater(3) and
    LTP<2.4*EntryPremium 
    )

#----------Exit Condition5 ------#
ExitCondition5=(
    DaystoExpiry(Expiry)==0 and
    EntryTimeGreater(3) and
    LTP<2.4*EntryPremium 
    )


PEIV=getGeeks("NIFTY","26SEP2024","impliedVolatility","SpotATM","CE")
SLPrem=GetFilledPremium*IVExitFactor*PEIV
orderUniqueIdentifier="Kohli"
 

        
   
    
