import time, traceback
import tweepy
import config
from tweepy import OAuthHandler
from sqlalchemy import create_engine, BigInteger, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

username = "postgres"
password = "password"
port = "5433"
db = "niche_users"

print ( "Connecting to database\n")
try:
	engine = create_engine("postgresql+psycopg2://{}:{}@localhost:{}/{}".format(username, password, port, db))

	print ( "Connected!\n" )
except:
	print ( "Connection Failed! \n")
	time.sleep(1.5)
	print(traceback.format_exc())

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

consumer_key = config.consumer_key
consumer_secret = config.consumer_secret
access_token = config.access_token
access_token_secret = config.access_token_secret
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
print(api)



class User(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(Text, unique=True)
    followers = Column(Integer)
    following = Column(Integer)
    user_id = Column(BigInteger, unique=True)
    tweet = Column(Text)

    def __repr__(self):
        return "<User(username='%s', followers='%s', following='%s')>" % (self.user_id, self.username, self.followers, self.following)