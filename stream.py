import datetime, threading, time, json, requests, langid, sys, traceback
import tweepy
from tweepy import Stream, OAuthHandler, StreamListener
from sqlalchemy import create_engine, Column, Integer, Float, Text, Boolean
from sqlalchemy import DateTime
from sqlalchemy import or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_declarative import Tweet, User, Price
from textblob import TextBlob

print("check your credentials")

consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

username = "postgres"
password = "postgres"
port = "5432"
db = "twitterbot"

print ( "Connecting to database\n")

engine = create_engine("postgresql+psycopg2://{}:{}@localhost:{}/{}".format(username, password, port, db))

print ( "Connected!\n" )

Base = declarative_base()
Session = sessionmaker(bind=engine)
global session
global auth
global api
session = Session()

count = 0
positive_count = 0
negative_count = 0
neutral_count  = 0
polarity_total = 0
polarity_average = 0
positive_polarity_average = 0
negative_polarity_average = 0
total = 0

def isTimeFormat(input):
    try:
        time.strptime(input, '%a %b %d %H:%M:%S +0000 %Y')

        return True
    except ValueError:

        return False

def get_sentiment(created_at, tweet_id, username, user_id, favorited, favorite_count, retweeted, retweet_count, followers, following, text):
    global count
    global positive_count
    global negative_count
    global neutral_count
    global polarity_total
    global polarity_average
    global positive_polarity_average
    global negative_polarity_average
    global total
    count += 1

    #timestamp = datetime.datetime.now()
    classify = langid.classify(text);
    lang = classify[0]

    if lang == "en":
        processed_text = TextBlob(text)
        sentiment = processed_text.sentiment
        polarity = sentiment.polarity
        polarity_total = polarity_total + polarity

        if polarity < 0:
            negative_count += 1
            #print("negative_count: {} \n".format(negative_count))
            negative_polarity_average = (9999*negative_polarity_average + polarity) / 10000
        elif polarity > 0:
            positive_count += 1
            #print("positive_count: {} \n".format(positive_count))
            positive_polarity_average = (9999*positive_polarity_average + polarity) / 10000
        elif polarity == 0.0:
            neutral_count += 1
            #print("neutral: {} \n".format(neutral_count))
        else:
            print("polarity is undefined \n")

        total = positive_count + negative_count + neutral_count
        if polarity != 0.0:
            polarity_average = (9999*polarity_average + polarity) / 10000

        print("Total processed: {}".format(total))
        print("Average positive sentiment: {}".format(positive_polarity_average))
        print("Average negative sentiment: {}".format(negative_polarity_average))
        print("Average sentiment: {}".format(polarity_average))
        print("Positive: {}".format(positive_count))
        print("Negative: {}".format(negative_count))
        print("Neutral: {} \n".format(neutral_count))

    else:
        #print("the tweet is not in english")
        return

     #http://stackoverflow.com/questions/5729500/how-does-sqlalchemy-handle-unique-constraint-in-table-definition
    # in order to get EST
    #print("90: " , created_at)
    #check the format and adjust accordingly
    #search method and stream method give different values for "created_at"
    if isTimeFormat(created_at):

        formatted_date = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(created_at,'%a %b %d %H:%M:%S +0000 %Y'))
        #http://stackoverflow.com/questions/9637838/convert-string-date-to-timestamp-in-python
        date_in_seconds = time.mktime(datetime.datetime.strptime(formatted_date, "%Y-%m-%d %H:%M:%S").timetuple())
        # subtract 5 hours from UTC to get EST
        adjusted_time = int(date_in_seconds) - 18000
        timestamp = datetime.datetime.fromtimestamp(adjusted_time).strftime('%Y-%m-%d %H:%M:%S')

    else:
        #print(formatted_date)
        timestamp = created_at

        
    user = session.query(User).filter(or_(User.user_id==user_id, User.username==username)).first()
    tweet = session.query(Tweet).filter_by(tweet_id=tweet_id).first()
    if user:
        if tweet:
            print(username)
        else:
            tweet_data = Tweet( tweet_id = tweet_id, user_id=user.id, text=text, retweet=retweeted, retweet_count=retweet_count, timestamp=timestamp, sentiment=polarity )
            session.add(tweet_data)
            session.commit()
    else:
        if tweet:
            print(username)
        else:
            user_data = User( user_id=user_id, username=username, followers=followers, following=following)
            session.add(user_data)
            session.commit()
            user = session.query(User).filter(or_(User.user_id==user_id, User.username==username)).first()
            tweet_data = Tweet( tweet_id=tweet_id, user_id=user.id, text=text, retweet=retweeted, retweet_count=retweet_count,timestamp=timestamp, sentiment=polarity )
            session.add(tweet_data)
            session.commit()

def process_data(data):
    tweet = json.loads(data)

    #output formatted json to the console
    #print( json.dumps( tweet, sort_keys=True, indent=4, separators=(',', ': ') ) )

    tweet_id = tweet['id']
    username = tweet['user']['screen_name']
    followers = tweet['user']['followers_count']
    following = tweet['user']['friends_count']
    retweeted = tweet['retweeted']
    retweet_count = tweet['retweet_count']
    favorited = tweet['favorited']
    favorite_count = tweet['favorite_count']
    created_at = tweet['created_at']
    user_id = tweet['user']['id']
    text = tweet['text']

    get_sentiment(created_at, tweet_id, username, user_id, favorited, favorite_count, retweeted, retweet_count, followers, following, text)


class listener(StreamListener):

    def on_data(self, data):
        process_data(data)

    def on_error(self, status):
        print( status.text )

#old way
'''
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
twitterStream = Stream(auth, listener())
while True:  #Endless loop: personalize to suit your own purposes
    try:
        twitterStream.filter(track=[
                                    "apple",
                                    "aapl",
                                    "imac",
                                    "ios",
                                    "ipad",
                                    "iphone",
                                    "ipod",
                                    "iwatch",
                                    "mac",
                                    "os x",
                                    "osx",
                                    "tim cook"
                                    ], languages=["en"]
                                )

    except:
        #e = sys.exc_info()[0]  #Get exception info (optional)
        #print ('ERROR:',e ) #Print exception info (optional)
        #print(traceback.format_exc())
        #print("sleeping")
        #time.sleep(1)
        twitterStream = Stream(auth, listener())
        continue
'''

def start_stream(twitterStream, keywords):
    while True:  #Endless loop: personalize to suit your own purposes
        try:
            twitterStream.filter(track=keywords, languages=["en"] )

        except:
            #e = sys.exc_info()[0]  #Get exception info (optional)
            #print ('ERROR:',e ) #Print exception info (optional)
            #print(traceback.format_exc())
            twitterStream = Stream(auth, listener())
            continue


auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
twitterStream = Stream(auth, listener())
api = tweepy.API(auth)

keywords = [
            
            "apple",
            "aapl",
            "imac",
            "ios",
            "ipad",
            "iphone",
            "ipod",
            "iwatch",
            "mac",
            "os x",
            "osx",
            "tim cook"

            ]

#prevent this function from starting again when fill.py is run
if __name__ == "__main__":
    start_stream(twitterStream, keywords)
