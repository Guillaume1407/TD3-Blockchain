# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 15:16:52 2020

@author: Miloj


ANANDARASA Milojan
BICHAT Guillaume
"""

import requests 
import json
from datetime import datetime
import sqlite3
import os.path
import calendar


products = requests.get('https://api.pro.coinbase.com/products')
products_json = json.loads(products.text)

currencies = requests.get('https://api.pro.coinbase.com/currencies')
currencies_json= json.loads(currencies.text)


"""
1)Get a list of all available cryptocurrencies and display it.


We have stored name and id of available crypto in a table.
We use print it in our Menu.

"""

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



###############################################################################

"""
2)Create a function to display the ’ask’ or ‘bid’ price of an asset. Direction and asset
name as parameters.

Function that returns the price of the direction that we choose. 
"""    
def getDepth(direction, pair):
    ticker=requests.get('https://api.pro.coinbase.com/products/'+pair+'/ticker')
    ticker_json=json.loads(ticker.text)
    return (ticker_json[direction])


###############################################################################

""" 
3)Get order book for an asset.
    
Return simply the order book in json format.

level corresponds to:
1	Only the best bid and ask
2	Top 50 bids and asks (aggregated)
3	Full order book (non aggregated)

"""
def order_book(pair,level):
    book = requests.get('https://api.pro.coinbase.com/products/'+pair+'/book?level='+level)
    book_json= json.loads(book.text)
    return book_json

###############################################################################

"""
4)Create a function to read agregated trading data (candles).
    
Return 300 values of trading data since a day that we choose.
"""
def refreshDataCandle(pair,duration,start):
    end=duration*300       #Can only read 300 values that's why we limit that
    end=start+end
    end=datetime.fromtimestamp(end).isoformat()               #Unix date to ISO date
    start=datetime.fromtimestamp(start).isoformat()
    candle=requests.get('https://api.pro.coinbase.com/products/'+str(pair)+'/candles?start='+str(start)+
                        '&end='+str(end)+'&granularity='+str(duration))
    candle_json=json.loads(candle.text)
    return candle_json
    
###############################################################################

"""
5)Create a sqlite table to store said data.
    
Here we choose the duration to create table candle and the start day for the 
other db.

"""
#Data candles
def create_table_in_candle(duration):
    connection=sqlite3.connect('Candle.db')
    cursor=connection.cursor()
    exchangeName="Coinbase"
    for x in products_json:
        pair=str(x['base_currency']+x['quote_currency'])
        TableName = str(exchangeName + "_" + pair + "_" + duration)
        tableCreationStatement = ("CREATE TABLE IF NOT EXISTS "+ TableName 
        +"(Id INTEGER PRIMARY KEY,date INT, high REAL, low REAL, open REAL, close REAL, volume REAL)")
        cursor.execute(tableCreationStatement)
    cursor.close()
    connection.close()


#Keeping track of updates:
def create_table_last_checks(start):
    if(os.path.isfile('Update.db')==False):
        connection=sqlite3.connect('Update.db')
        cursor=connection.cursor()    
        Id=1
        cursor.execute("CREATE TABLE IF NOT EXISTS last_checks(Id INTEGER PRIMARY KEY," 
                                                               +"exchange TEXT, trading_pair TEXT ,duration TEXT,table_name TEXT, "
                                                               +"last_check INT,startdate INT,last_id INT)")
        cursor.close()
        connection.commit()
        cursor2=connection.cursor()
        for x in products_json:
            insert=('INSERT INTO last_checks VALUES ('+str(Id)+',"'+str('Coinbase')
                    +'","'+str(x['base_currency']+x['quote_currency'])+'","'+str('5m')+'","'
                    +str('Coinbase'+ "_" + x['base_currency']+x['quote_currency'] + "_" + '5m')
                    +'",'+str(start)+','+str(start)+','+str(0)+')')                  
            Id=Id+1
            cursor2.execute(insert)
            connection.commit()
        cursor2.close()
        connection.close()                                               

###############################################################################

"""
6)Store candle data in the db.
7)Modify function to update when new candle data is available.

To update new candle we use a recursive function that read the two before databases
and know if the database is update or not.

"""
def insert_data_in_candle(tablename,pair,duration):
        
    connection3=sqlite3.connect('Update.db')    #Second database
    cursor3=connection3.cursor()
    select1="SELECT last_check FROM last_checks WHERE table_name='"+ str(tablename)+"'"
    cursor3.execute(select1)
    start=cursor3.fetchall() 
    start=start[0][0]
    
    data=refreshDataCandle(pair,duration,start)            #import the data from a day that we choose
    if not data:                   #Check if our data is not empty 
        exit()
    
    connection=sqlite3.connect('Candle.db')    #Fisrt database 
    cursor=connection.cursor()
    
    connection2=sqlite3.connect('Update.db') 
    cursor2=connection2.cursor()
    
    last_check=0
    select="SELECT last_id FROM last_checks WHERE table_name='"+ str(tablename)+"'"
    cursor2.execute(select)
    last=cursor2.fetchall()            #collect the last id of the database
    n=1+last[0][0]
    cursor2.close()
    
    for x in data:
        insert=("INSERT INTO "+tablename+"(Id,date,high,low,open,close,volume) " 
                +"VALUES ("+str(n)+","+str(x[0])+","+str(x[2])+","+str(x[1])+","+str(x[3])+","+str(x[4])+","+str(x[5])+")")
        cursor.execute(insert)
        connection.commit()
        last_check=x[0]              #collect always the last id to store it in our database update
        n=n+1
    
    if(last_check!=0):
        cursor2=connection2.cursor()
        cursor2.execute('Update last_checks set last_check='+str(last_check)+', last_id='+str(n-1)+ ' where table_name="'+tablename+'"')
        connection2.commit()                                  #cursor2.execute(...) store last id 
        cursor2.close()
        
    cursor.close()
    connection.close()
    connection2.close()
    insert_data_in_candle(tablename,pair,duration)      #redo the function until 
                                                                              #that the data is not empty


###############################################################################

"""
8)Create a function to extract all available trade data.
9)Store the data in sqlite.
        
In the same way that the previous function: implement database and fill it with 
data
"""


#Full data set:
def create_table_full_data(pair):
    connection=sqlite3.connect('Full_data.db')
    cursor=connection.cursor()  
    TableName = str( "Coinbase_" + pair)
    tableCreationStatement = ("CREATE TABLE IF NOT EXISTS " +TableName + "(Id INTEGER PRIMARY KEY, "
    +"uuid TEXT, traded_btc REAL, price REAL, created_at INT, side TEXT)")
    cursor.execute("DROP TABLE "+TableName)           #If we havce already data in this table 
    connection.commit()                               #we remove all and replace it by the new data  
    cursor.close()
    cursor2=connection.cursor()  
    cursor2.execute(tableCreationStatement)
    connection.commit()
    cursor2.close()
    connection.close()



def refreshData(pair):
    create_table_full_data(pair)
    trades = requests.get('https://api.pro.coinbase.com/products/BTC-USD/trades')   #Full data of BTC-USD
    trades_json = json.loads(trades.text)
    
    connection=sqlite3.connect('Full_data.db')
    cursor=connection.cursor()
    
    n=1
    tablename="Coinbase_"+pair

    for x in trades_json:
        time=x['time'][:-1]
        time=calendar.timegm(datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f").timetuple())  #ISO date to Unix date 
        insert=("INSERT INTO "+tablename+"(Id,uuid,traded_btc,price,created_at,side) "
                +"VALUES("+str(n)+",'"+str(x['trade_id'])+"',"+str(x['size'])+","
                +str(x['price'])+","+str(time)+",'"+str(x['side'])+"')")
        cursor.execute(insert)
        connection.commit()
        n=n+1
    cursor.close()
    connection.close()
    
###############################################################################
"""
Launch programs
"""

#print(order_book('BTC-USD',str(2)))    #Uncomment to see

"""
We join a preview of database for BTC-USD on 5m in our github
"""
create_table_last_checks(1579910400) #1579910400=2020-01-25
create_table_in_candle("5m")
insert_data_in_candle('Coinbase_BTCUSD_5m','BTC-USD',300)  #300=5m
"""refreshData('BTCUSD')   """                                              


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
            n=n+1
            
        print("                           ##########################################\n")
        print("1)Ask or 2)Bid price of BTC-USD")    
        choix=input("Tapez votre choix: ")
        if(choix==str(1)):
            print(getDepth(direction='ask', pair ='BTC-USD'))
        if (choix==str(2)):
            print(getDepth(direction='bid', pair ='BTC-USD'))

            
            
