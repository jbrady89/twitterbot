import datetime, threading, time, json, requests, langid, sys
from tweepy import Stream, OAuthHandler, StreamListener
from sqlalchemy import create_engine, Column, Integer, Float, Text, Boolean
from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_declarative import Price, Tweet, User
from textblob import TextBlob

print ( "Connecting to database\n" )

engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/twitterbot")

print ( "Connected!\n" )

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

