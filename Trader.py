from binance.client import Client
import talib as ta
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import math
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import pytz
import dateparser
import logging
from decimal import Decimal

class CoinList:
    CoinName=""
    CoinAmount=""
    USDTAmount=""
    Strategy=""
    CoinBotOnOff="on"
    GraphDuration = ""
    BotType = ""
   
class ApiKeyPair:
    ApiKey=""
    Secret=""
 
class TillSonParam:
    VolumeFactor=0.0
    Length=0
    
class SuperTrendParam:
    Period=0
    Multiplier=0.0

class MACDParam:
    FastPeriod=0
    SlowPeriod=0
    SignalPeriod=0
    
    
    
import base64
from Crypto.Cipher import AES

BS = 16
pad = lambda s: bytes(s + (BS - len(s) % BS) * chr(BS - len(s) % BS), 'utf-8')
unpad = lambda s : s[0:-ord(s[-1:])]
class AESCipher:

    def __init__( self, key ):
        self.key = bytes(key, 'utf-8')

    def encrypt( self, raw ):
        raw = pad(raw)
        iv = "9/\~V).A,lY&=t2b".encode('utf-8')
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return base64.b64encode(cipher.encrypt( raw ) )
    
    def decrypt( self, enc ):
        iv = "9/\~V).A,lY&=t2b".encode('utf-8')
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc )).decode('utf8')
    
class BinanceConnection:
    def __init__(self, apiKey, secret):
        try:
            self.connect(apiKey, secret)
        except BaseException as error:
            logMeError('An exception occurred: {}'+format(error))

    """ Creates Binance client """

    def connect(self, apiKey, secret):        
        try:
            self.client = Client(apiKey, secret)
        except BaseException as error:
            logMeError('An exception occurred: {}'+format(error))


def generateTillsonT3(close_array, high_array, low_array, volume_factor, t3Length):
    try:
        ema_first_input = (high_array + low_array + 2 * close_array) / 4

        e1 = ta.EMA(ema_first_input, t3Length)

        e2 = ta.EMA(e1, t3Length)

        e3 = ta.EMA(e2, t3Length)

        e4 = ta.EMA(e3, t3Length)

        e5 = ta.EMA(e4, t3Length)

        e6 = ta.EMA(e5, t3Length)

        c1 = -1 * volume_factor * volume_factor * volume_factor

        c2 = 3 * volume_factor * volume_factor + 3 * volume_factor * volume_factor * volume_factor

        c3 = -6 * volume_factor * volume_factor - 3 * volume_factor - 3 * volume_factor * volume_factor * volume_factor

        c4 = 1 + 3 * volume_factor + volume_factor * volume_factor * volume_factor + 3 * volume_factor * volume_factor

        T3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3

        return T3
    except BaseException as error:
        logMeError('An exception occurred: {}'+format(error))
 

def generateSupertrend(close_array, high_array, low_array, atr_period, atr_multiplier):
    try:
    
        atr = ta.ATR(high_array, low_array, close_array, atr_period)
    

        previous_final_upperband = 0
        previous_final_lowerband = 0
        final_upperband = 0
        final_lowerband = 0
        previous_close = 0
        previous_supertrend = 0
        supertrend = []
        supertrendc = 0

        for i in range(0, len(close_array)):
            if np.isnan(close_array[i]):
                pass
            else:
                highc = high_array[i]
                lowc = low_array[i]
                atrc = atr[i]
                closec = close_array[i]

                if math.isnan(atrc):
                    atrc = 0

                basic_upperband = (highc + lowc) / 2 + atr_multiplier * atrc
                basic_lowerband = (highc + lowc) / 2 - atr_multiplier * atrc

                if basic_upperband < previous_final_upperband or previous_close > previous_final_upperband:
                    final_upperband = basic_upperband
                else:
                    final_upperband = previous_final_upperband

                if basic_lowerband > previous_final_lowerband or previous_close < previous_final_lowerband:
                    final_lowerband = basic_lowerband
                else:
                    final_lowerband = previous_final_lowerband

                if previous_supertrend == previous_final_upperband and closec <= final_upperband:
                    supertrendc = final_upperband
                else:
                    if previous_supertrend == previous_final_upperband and closec >= final_upperband:
                        supertrendc = final_lowerband
                    else:
                        if previous_supertrend == previous_final_lowerband and closec >= final_lowerband:
                            supertrendc = final_lowerband
                        elif previous_supertrend == previous_final_lowerband and closec <= final_lowerband:
                            supertrendc = final_upperband

                supertrend.append(supertrendc)

                previous_close = closec

                previous_final_upperband = final_upperband

                previous_final_lowerband = final_lowerband

                previous_supertrend = supertrendc

        return supertrend
    except BaseException as error:
        logMe('An exception occurred: {}'+format(error))
 

 
def getCoinList(graphicDuration):
    try:
        coins = []

        with open('coinList.txt', 'r') as coinList:
            coinList = coinList.readlines()

        for row in coinList:
            if(row.startswith('#')):
                continue
       
            vals = row.split(':')
            if(vals[6]!=graphicDuration):
                continue
            coin = CoinList()
           
            coin.CoinName = vals[0]
            coin.CoinAmount = vals[1]
            coin.USDTAmount = vals[2]
            coin.Strategy = vals[3]
            coin.CoinBotOnOff = vals[4]
            coin.BotType = vals[5]
            coin.GraphDuration = graphicDuration
            coins.append(coin)
            
        return coins    
    except BaseException as error:
        logMeError('An exception occurred: {}'+format(error))
        raise
 

def date_to_milliseconds(date_str):
    """Convert UTC date to milliseconds
    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/
    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    :type date_str: str
    """
    # get epoch value in UTC
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    # parse our date string
    d = dateparser.parse(date_str)
    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    # return the difference in time
    return int((d - epoch).total_seconds() * 1000.0)

 
def analyzeSymbolWithT3(klines, _coin, tillSonParams):
    try:
        pair = _coin.CoinName
        open_time = [int(entry[0]) for entry in klines]

        open = [float(entry[1]) for entry in klines]
        high = [float(entry[2]) for entry in klines]
        low = [float(entry[3]) for entry in klines]
        close = [float(entry[4]) for entry in klines]

        last_closing_price = close[-1]
        last_open_price = open[-1]

        previous_closing_price = close[-2]

        logMe(pair+' last_closing_price ' +str(last_closing_price)+ ', previous_closing_price '+ str(previous_closing_price))

        close_array = np.asarray(close)
        high_array = np.asarray(high)
        low_array = np.asarray(low)


        volume_factor = float(tillSonParams.VolumeFactor) # 1   #0.7
        length = int(tillSonParams.Length)

        tillsont3 = generateTillsonT3(close_array, high_array, low_array, volume_factor=volume_factor, t3Length=length)
        
        t3_last = tillsont3[-1]
        t3_previous = tillsont3[-2]
        t3_prev_previous = tillsont3[-3]
            
        
        if t3_last > t3_previous and t3_previous < t3_prev_previous:
            print('Buy signal,'+pair)
        
        elif t3_last < t3_previous and t3_previous > t3_prev_previous:
            print('Sell signal,'+pair)

    except BaseException as error:
        logMeError('An exception occurred: {}'+format(error))
        
def analyzeSymbolWithMACD(klines, _coin, MACDParams):
    try:
        pair = _coin.CoinName
        logMe("MACD analyze. "+pair)

        open_time = [int(entry[0]) for entry in klines]

        open = [float(entry[1]) for entry in klines]
        high = [float(entry[2]) for entry in klines]
        low = [float(entry[3]) for entry in klines]
        close = [float(entry[4]) for entry in klines]

        last_closing_price = close[-1]
        last_open_price = open[-1]

        previous_closing_price = close[-2]

        close_array = np.asarray(close)
        high_array = np.asarray(high)
        low_array = np.asarray(low)
    
        close_finished = close_array[:-1]

        macd, macdsignal, macdhist = ta.MACD(close_finished, fastperiod=MACDParams.FastPeriod, slowperiod=MACDParams.SlowPeriod, signalperiod=MACDParams.SignalPeriod)
        #rsi = ta.RSI(close_finished, timeperiod=14)

        logMe(str(len(macd))+ " macdlen")

        if len(macd) > 0:
            last_macd = macd[-1]
            last_macd_signal = macdsignal[-1]

            previous_macd = macd[-2]
            previous_macd_signal = macdsignal[-2]

       

            logMe(" macdlast: "+str(last_macd)+ " last_macd_signal" + str(last_macd_signal) )
            logMe(" previous_macd: "+str(previous_macd)+ " previous_macd_signal" + str(previous_macd_signal) )
            
            macd_cross_up = last_macd > last_macd_signal and previous_macd < previous_macd_signal
            macd_cross_do = last_macd < last_macd_signal and previous_macd > previous_macd_signal
            
            if macd_cross_up:
                print('Buy signal,'+pair)    
            elif macd_cross_do:
                print('Sell signal,'+pair)
    except BaseException as error:
        logMeError('An exception occurred: {}'+format(error))

def analyzeSymbolWithST(klines,  _coin, STParams):
    try:
            
        pair = _coin.CoinName
        open_time = [int(entry[0]) for entry in klines]

        open = [float(entry[1]) for entry in klines]
        high = [float(entry[2]) for entry in klines]
        low = [float(entry[3]) for entry in klines]
        close = [float(entry[4]) for entry in klines]

        

        last_closing_price = close[-1]
        #last_open_price = open[-1]

        previous_closing_price = close[-2]


        logMe(pair+' last_closing_price ' +str(last_closing_price)+ ', previous_closing_price '+ str(previous_closing_price))

        close_array = np.asarray(close)
        high_array = np.asarray(high)
        low_array = np.asarray(low)
    
        supertrend = generateSupertrend(close_array, high_array, low_array, atr_period=STParams.Period, atr_multiplier=STParams.Multiplier)

        lastCloseVal = close_array[-1]
        previousCloseVal = close_array[-2]

        lastSTVal = supertrend[-1]
        previousSTVal = supertrend[-2]

        if lastCloseVal > lastSTVal and previousCloseVal < previousSTVal:
            print('Buy signal,'+pair)


        if lastCloseVal < lastSTVal and previousCloseVal > previousSTVal:
            print('Sell signal,'+pair)
    except BaseException as error:
        logMeError('An exception occurred: {}'+format(error))
 
def getInterval(strategy, graphicDuration,time_res):
       
        
        interval = Client.KLINE_INTERVAL_1DAY
       
        
        endTm = -60*60*24*1000 - 30000 # for default 1 day
      
        if(graphicDuration=="5m"):
            interval = Client.KLINE_INTERVAL_5MINUTE
            if(strategy=="T1" or strategy=="ST"):
                endTm = time_res- 60*5*1000 #  minus 5 min 
            
            elif(strategy=="M"):
                endTm = time_res #  minus 5 min - 10 sec              
                
        elif(graphicDuration=="15m"): 
            interval = Client.KLINE_INTERVAL_15MINUTE
            if(strategy=="T1"):
                endTm = time_res- 60*15*1000  #  minus 15 min - 10 sec
            elif(strategy=="ST"):
                endTm = time_res 
            elif(strategy=="M"):
                endTm = time_res 
                
        elif(graphicDuration=="30m"):
            interval = Client.KLINE_INTERVAL_30MINUTE
            
            if(strategy=="T1"):
                endTm = time_res- 60*30*1000 #  minus 30 min - 10 sec
            elif(strategy=="ST"):
                endTm = time_res 
            elif(strategy=="M"):
                endTm = time_res  
            
        elif(graphicDuration=="1h"):
            interval = Client.KLINE_INTERVAL_1HOUR 
            
            if(strategy=="T1"):
                endTm = time_res- 60*60*1000  #  minus 60 min - 10 sec
            elif(strategy=="ST"):
                endTm = time_res 
            elif(strategy=="M"):
                endTm = time_res 
            
            
        elif(graphicDuration=="2h"):
            interval = Client.KLINE_INTERVAL_2HOUR 
            if(strategy=="T1"):
                endTm = time_res- 60*60*2*1000  #  minus 2*60 min - 10 sec
            elif(strategy=="ST"):
                endTm = time_res 
            elif(strategy=="M"):
                endTm = time_res              
                
        elif(graphicDuration=="3h"): #Binance desteklemiyor
            interval = '3h'
            if(strategy=="T1"):
                endTm = time_res- 60*60*3*1000  #  minus 2*60 min - 10 sec
            elif(strategy=="ST"):
                endTm = time_res 
            elif(strategy=="M"):
                endTm = time_res     
        
        elif(graphicDuration=="4h"):
            interval = Client.KLINE_INTERVAL_4HOUR   
            if(strategy=="T1"):
                endTm = time_res- 60*60*4*1000  #  minus 2*60 min - 10 sec
            elif(strategy=="ST"):
                endTm = time_res 
            elif(strategy=="M"):
                endTm = time_res            
                
        elif(graphicDuration=="1d"):
            interval = Client.KLINE_INTERVAL_1DAY   
         
            if(strategy=="T1"):
                endTm = time_res- 60*60*24*1000  #  minus 2*60 min - 10 sec
            elif(strategy=="ST"):
                endTm = time_res 
            elif(strategy=="M"):
                endTm = time_res    
        elif(graphicDuration=="2d"):
            interval = '2d' 
         
            if(strategy=="T1"):
                endTm = time_res- 60*60*48*1000  #  minus 2*60 min - 10 sec
            elif(strategy=="ST"):
                endTm = time_res
            elif(strategy=="M"):
                endTm = time_res
    
        logMe("-------> Server Zamanı <--------"+str(datetime.fromtimestamp(time_res/1000.0)))
        logMe("-------> Çubuk Zamanı <--------"+str(datetime.fromtimestamp(endTm/1000.0)))
        return interval, endTm
    
def analyzeSymbol(graphicDuration, time_res):
    try:
            
    
        coinList = getCoinList(graphicDuration)
 
        apiKey = getApiKey()
        
        if(apiKey.ApiKey==""):
            return
        
        connection = BinanceConnection(apiKey.ApiKey, apiKey.Secret)
 
        for _coin in coinList:
            try:
            
            
                logMe("Coin Name "+_coin.CoinName +"Coin Strategy:"+_coin.Strategy+ " BotOnOff:"+_coin.CoinBotOnOff)
                limit=500
                
                interval, endTm =getInterval(_coin.Strategy, graphicDuration,time_res) 
                klines = connection.client.get_klines(symbol=_coin.CoinName, interval=interval, limit=limit, endTime=endTm)

                if(_coin.Strategy=="T1" and _coin.CoinBotOnOff=="on"):
                  
                    tillSonParams = TillSonParam()
                    tillSonParams.Length = 8
                    tillSonParams.VolumeFactor = 0.7
                    
                    analyzeSymbolWithT3(klines, _coin, tillSonParams)
                    
                elif(_coin.Strategy=="ST" and _coin.CoinBotOnOff=="on"): 
                         
                    STParam = SuperTrendParam()
                    STParam.Multiplier = 3
                    STParam.Period = 10
                    
                    analyzeSymbolWithST(klines, _coin,STParam)
                elif(_coin.Strategy=="M" and _coin.CoinBotOnOff=="on"):  
 
                    MACDParams = MACDParam()
                    MACDParams.FastPeriod = 11
                    MACDParams.SignalPeriod = 8 
                    MACDParams.SlowPeriod = 25
                    
                    analyzeSymbolWithMACD(klines,_coin,MACDParams)
            except BaseException as error:
                logMeError('An exception occurred: {}'+format(error))
                
                
    except BaseException as error:
        logMeError('An exception occurred: {}'+format(error))

def parse_line(line):
    delim_loc = line.find(':')
    return line[delim_loc+1:].strip()

def read_config(config_string):
    apiKey = parse_line(config_string[0])
    secret = parse_line(config_string[1])
    return  apiKey, secret 
 
def getApiKey():
    try:
        cipher = AESCipher("qwr{@^h`h&_`50/ja9!'dcmh3!uw<&=?")
         
        with open('config.txt', 'r') as config:
            config_values = config.readlines()

        apiKey, secret = read_config(config_values)

        inApiKey= ApiKeyPair() 
        inApiKey.ApiKey =  cipher.decrypt(apiKey)
        inApiKey.Secret =  cipher.decrypt(secret)
        
        return inApiKey
           
    except BaseException as error:
        logMeError('An exception occurred: {}'+format(error))   
    
def jobDef(graphDuration):
    try:
        
        
        apiKey = getApiKey()
        connection = BinanceConnection(apiKey.ApiKey, apiKey.Secret)

        dictTimeRes = connection.client.get_server_time()
        time_res = dictTimeRes['serverTime'] 

        analyzeSymbol(graphDuration, time_res)
                
    except BaseException as error:
        logMeError('An exception occurred: {}'+format(error))  

def logMe(msg):
    logging.info(msg)
    # print(msg)

def logMeError(msg):
    logging.info("------->ERROR!!!!!!<-------"+msg)
    print(msg)
    
#run setup and copy/paste values inside quotes to config.txt
def setup():
        
    cipher = AESCipher("qwr{@^h`h&_`50/ja9!'dcmh3!uw<&=?")
    apiKey = 'yourApiKey'
    secret = 'yourSecret'
    print(cipher.encrypt(apiKey))
    print(cipher.encrypt(secret))
    

if __name__ == '__main__':

    logging.basicConfig(handlers=[logging.FileHandler(filename="./logs.log", 
                                                encoding='utf-8', mode='a+')],
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s", 
                    datefmt="%F %A %T", 
                    level=logging.INFO)   

   
    now = datetime.now()
    nowStr = now.strftime("%Y-%m-%d")+' 00:00:00'
    logMe("################## "+nowStr)
    logMe("#########################################")
    
    #setup()

    scheduler = BlockingScheduler()
    #jobDef('5m')
    # add jobs to candle starts (or ends)
    scheduler.add_job(jobDef, 'interval', minutes=5,start_date=nowStr,kwargs={'graphDuration': '5m'})
    scheduler.add_job(jobDef, 'interval', minutes=15,start_date=nowStr,kwargs={'graphDuration': '15m'})
    scheduler.add_job(jobDef, 'interval', minutes=30,start_date=nowStr,kwargs={'graphDuration': '30m'})
    scheduler.add_job(jobDef, 'interval', hours=1,start_date=nowStr,kwargs={'graphDuration': '1h'})
    scheduler.add_job(jobDef, 'interval', hours=2,start_date=nowStr,kwargs={'graphDuration': '2h'})
    scheduler.add_job(jobDef, 'interval', hours=3,start_date=nowStr,kwargs={'graphDuration': '3h'})
    scheduler.add_job(jobDef, 'interval', hours=4,start_date=nowStr,kwargs={'graphDuration': '4h'})
    scheduler.add_job(jobDef, 'interval', hours=24,start_date=nowStr,kwargs={'graphDuration': '1d'})
    scheduler.add_job(jobDef, 'interval', hours=48,start_date=nowStr,kwargs={'graphDuration': '2d'})
 
    scheduler.start()