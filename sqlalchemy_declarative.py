import os
import sys, datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, Text, Boolean, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()
class Price(Base):
	__tablename__ = 'prices'

	id = Column(Integer, primary_key=True, index=True)
	#symbol = Column(String)
	close = Column(Float)
	timestamp = Column(DateTime, default=datetime.datetime.now(), index=True, unique=True)

	def __repr__(self):
		return "<User(close='%s')>" % (self.close)

class Tweet(Base):
	__tablename__ = 'tweets'

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(BigInteger, index=True)
	text = Column(Text)
	retweet = Column(Boolean)
	retweet_count = Column(Integer)
	timestamp = Column(DateTime, default=datetime.datetime.now(), index=True)
	sentiment = Column(Float)


	def __repr__(self):
		return "<Tweet(user_id = {}, text= {}, retweet={}, retweet_count={}, timestamp={}, sentiment={})>".format(self.user_id, self.text, self.retweet, self.retweet_count, self.timestamp, self.sentiment)

class User(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True, index=True)
	username = Column(Text, unique=True)
	followers = Column(Integer)
	following = Column(Integer)

	def __repr__(self):
		return "<User(username='%s', followers='%s', following='%s')>" % (self.username, self.followers, self.following)