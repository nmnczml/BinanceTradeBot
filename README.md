# BinanceTradeBot
Binance Trading bot with Tillson, SuperTrend and MACD algorithms, a small snapshot from my bigger project. Uses https://github.com/sammchardy/python-binance project. 

# Installation
Follow Quick Start steps of https://github.com/sammchardy/python-binance project.<br>
Replace your ApiKey, Secret credentials in setup function of Trader.py and run setup function.<br>
Change the coinList.txt according to the method you want to apply.<br>

# CoinList.txt 
CoinName: Coin pair like ETHUSDT, BTCUSDT etc.<br>
CoinAmount: Start amount of coin to trade. <br>
USDTAmount: Start amount of USDT to trade.<br>
Strategy: M for MACD, T1 for Tillson, ST for SuperTrend<br>
BotOnOff: "on" for open, "off" for close the bot<br>
BotType: "S" for simulation. <Will be changed after for real coin trade><br>
GraphDuration: Candle stick patterns for bot to run after. 5m, 15m, 30m, 1h, 2h, 3h, 4h, 1d and 2d.<br>
