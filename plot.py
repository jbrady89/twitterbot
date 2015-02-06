
import datetime, threading, time, json, requests, langid, sys, traceback
from tweepy import Stream, OAuthHandler, StreamListener
from sqlalchemy import create_engine, Column, Integer, Float, Text, Boolean
from sqlalchemy import DateTime
from sqlalchemy import or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_declarative import Tweet, User, Price
from textblob import TextBlob
from itertools import islice
import matplotlib
from matplotlib import pyplot as plt
import numpy as np

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

def window(seq, n=1000):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result

def moving_averages(values, size):
    for selection in window(values, size):
        yield sum(selection) / size

sentiments = []
sentiment_MAs = []
tweets = session.query(Tweet).all()

print("processing tweet sentiment...\n")

for tweet in tweets:
	sentiments.append(tweet.sentiment)

print(sentiments)

print("calculating moving averages...\n")

for avg in moving_averages(sentiments, 1000):
	sentiment_MAs.append(avg)

print(sentiment_MAs)

#plot sentiment moving average over the length of the array
length = len(sentiment_MAs)
y = sentiment_MAs
x = np.arange(0, length)
plt.xlim(0,length)
plt.ylim(-1,1)

plt.plot(x, y, ".")
plt.show()
