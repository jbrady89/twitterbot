import datetime, threading, time, json, requests, langid, sys
from tweepy import Stream, OAuthHandler, StreamListener
from sqlalchemy import create_engine, Column, Integer, Float, Text, Boolean
from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_declarative import Price, Tweet, User
from textblob import TextBlob

<<<<<<< HEAD
print ( "Connecting to database\n" )

engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/twitterbot")
=======
username = "postgres"
password = "postgres"
port = "5432"
db = "twitterbot"

print ( "Connecting to database\n")

engine = create_engine("postgresql+psycopg2://{}:{}@localhost:{}/{}".format(username, password, port, db))
>>>>>>> 977d8880ee9c01cc13bc794c1cbdc7c704068c96

print ( "Connected!\n" )

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

