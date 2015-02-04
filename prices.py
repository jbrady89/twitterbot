import datetime, threading, time, json, requests, langid, sys
from tweepy import Stream, OAuthHandler, StreamListener
from sqlalchemy import create_engine, Column, Integer, Float, Text, Boolean
from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_declarative import Price, Tweet
from textblob import TextBlob

username = "postgres"
password = "password"
port = "5433"
db = "twitterbot"

print ( "Connecting to database\n")

engine = create_engine("postgresql+psycopg2://{}:{}@localhost:{}/{}".format(username, password, port, db))

print ( "Connected!\n" )

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

next_call = time.time()
last_price = None

#gets minute data for up to the last 15 days
def get_historic_data(symbol):
    response = requests.get("http://chartapi.finance.yahoo.com/instrument/1.1/{}/chartdata;type=close;range=1d;/json/".format(symbol))
    jsonp = response.text
    fixed_json = jsonp[ jsonp.index("(") + 1 : jsonp.rindex(")") ]
    price_data = json.loads(fixed_json)
    #loop through the minute data
    #it is 5 minute data when range is > 1d
    for entry in price_data['series'][:-1]:
        close = entry["close"]
        timestamp = entry["Timestamp"]
        timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        price = session.query(Price).filter_by(timestamp=timestamp).first()
        if price: 
            print("a record exists with the time value: {} \n".format(time))
        else:
            price = Price(close=close, timestamp=timestamp)
            session.add(price)
            session.commit()
            print("Close: {}, Timestamp: {} \n".format(close, timestamp))

def get_stock_data():
    global last_price
    response = requests.get("http://finance.yahoo.com/webservice/v1/symbols/AAPL/quote?format=json")
    json_data = response.json()

    close = json_data['list']['resources'][0]['resource']['fields']['price']
    timestamp = time.time()
    timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    time_exists = session.query(Price).filter_by(timestamp=timestamp).first()
    if time_exists:
        print("a record exists with the time value: {} \n".format(time_exists))
    else:
        #insert data
        price = Price(close=close, timestamp=timestamp)
        session.add(price)
        session.commit()
        print("Close: {}, Timestamp: {} \n".format(close, timestamp))

def get_quote():
    global next_call
    #the current time
    print ( time.time() ) 
    get_stock_data() #get the current price
    next_call = next_call + 1.00 #schedule the next call for 1 minute in the future
    #this sets up the 1 minute interval running in the background
    price_timer = threading.Timer( next_call - time.time(), get_quote )
    price_timer.start()

def get_bloomberg_data(symbol):

    response = requests.get("http://www.bloomberg.com/markets/chart/data/1D/{}:US".format(symbol))
    json_response = response.json()
    bloomberg_data = json_response["data_values"]
    for price in bloomberg_data:
        thetime = price[0] / 1000
        timestamp = datetime.datetime.fromtimestamp(thetime).strftime('%Y-%m-%d %H:%M:%S:%f')        
        close = price[1]
        print("Time: {}, Close: {}".format(timestamp, close))

def get_data_from_period(period):
    #to get all prices since a certain time 
    #this returns all rows with a timestamp after or equal to the specified
    period = session.query(Price).filter(Price.timestamp >= period)
    period = period.all()
    for data in period: 
        print(data.close)
        print(data.timestamp)


#get_historic_data("AAPL")
get_data_from_period('2015-2-3 15:00:0')
#get_bloomberg_data("AAPL")
#next_call = time.time()
#get_quote()