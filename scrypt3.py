# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 15:16:52 2020

@author: Miloj
"""

import requests 
import json
from datetime import datetime
import sqlite3


products = requests.get('https://api.pro.coinbase.com/products')
products_json = json.loads(products.text)

currencies = requests.get('https://api.pro.coinbase.com/currencies')
currencies_json= json.loads(currencies.text)


def available_crypto():
    tab=[[],[]]
    for i in products_json:
        if(not (i['base_currency'] in tab[0])):
            tab[0].append(i['base_currency'])
    
    for x in tab[0]:
        for y in currencies_json:
            if(x==y['id']):
                tab[1].append(y['name'])       
    return (tab)
    
def getDepth(direction='ask', pair ='BTC-USD'):
    ticker=requests.get('https://api.pro.coinbase.com/products/'+pair+'/ticker')
    ticker_json=json.loads(ticker.text)
    return (ticker_json[direction])
    
def order_book(pair,level):
    book = requests.get('https://api.pro.coinbase.com/products/'+pair+'/book?level='+level)
    book_json= json.loads(book.text)
    return book_json


def refreshDataCandle(pair,duration,start):
    end=duration*300
    end=start+end
    candle=requests.get('https://api.pro.coinbase.com/products/'+pair+'/candles?start='+start+
                        '&end='+end+'&granularity='+duration)
    candle_json=json.loads(candle.text)
    return candle_json
    

"""def connection_db():
    connection=sqlite3.connect()
    cursor=connection.cursor()
    #Keeping track of updates:
    cursor.execute("CREATE TABLE IF NOT EXISTS last_checks(Id INTEGER PRIMARY KEY, " 
                +"exchange TEXT,trading_pair TEXT , duration TEXT, table_name TEXT, "
                +"last_check INT, startdate INT,last_id INT)");
    

    #Data candles:
    setTableName = str(exchangeName + "_" + pair + "_" + duration)
    tableCreationStatement = "CREATE TABLE "+ setTableName + "(Id INTEGER PRIMARY KEY, "
    +"date INT, high REAL, low REAL, open REAL, close REAL, volume REAL)"

    #Full data set:
    setTableName = str(exchangeName + "_" + pair)
    tableCreationStatement = "CREATE TABLE " +setTableName + "(Id INTEGER PRIMARY KEY, uuid TEXT, traded_btc REAL, price REAL, created_at_int INT, side TEXT)"
"""
"print(datetime.fromtimestamp(1580304600).isoformat())"
"""refreshDataCandle(pair = 'BTC-USD',duration =str(300))
order_book('BTC-USD',str(2))
available_crypto()
getDepth(direction='ask', pair ='BTC-USD')"""








""" 
         MENU
"""
def Menu():
    crypto=available_crypto()
    choix=0
    while(choix!=3):
        n=1
        print("\n                               ##################################\n")
        print("                                      Cryptocurrencies: \n")
        print("                               ##################################\n")
        print("Which one do you want to use?\n")
        for x in crypto[0]:
            print(str(n)+") "+ x+" : "+crypto[1][crypto[0].index(x)])
            
        print("                           ##########################################\n")
        print("Tapez votre choix: ")      
        choix=input()

        if(choix==str(1)):
            Creer_seed()
        
        if(choix==str(2)):
            option=0
            myseed=Seed_mnemonic()
            while(option!=str(3)):
                    print("Veuillez choisir votre option parmi 1, 2 ou 3")
        
        if(choix==str(3)):
                return 0;
    
        if(choix!=str(3) and choix !=str(2) and choix!=str(1)):
            print("Veuillez choisir votre option parmi 1, 2 ou 3")