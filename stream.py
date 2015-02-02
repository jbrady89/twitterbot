import datetime, threading, time, json, requests, langid, sys, traceback
from tweepy import Stream, OAuthHandler, StreamListener
from sqlalchemy import create_engine, Column, Integer, Float, Text, Boolean
from sqlalchemy import DateTime
from sqlalchemy import or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_declarative import Tweet, User, Price
from textblob import TextBlob

<<<<<<< HEAD
consumer_key = "rY3Q4lLIAcLRXPm66JoU2jL8X"
consumer_secret = "xkTrpkamaiDQaiAdEvcvJLj6hmaLH0DL2m5bE4l4H7ROFuRKBC"
access_token = "928665026-VghhFE4Xxovwv1Sz7Ivizdm6bGjEQn2yFGgd5TIy"
access_token_secret = "xtdeTR1eEkSwlhPwj02OLle64kPFvBUYgfx9FsuaozZdI"

=======
# check your credentials
print("check your credentials")

consumer_key = "rY3Q4lLIAcLRXPm66JoU2jL8X"
consumer_secret = "xkTrpkamaiDQaiAdEvcvJLj6hmaLH0DL2m5bE4l4H7ROFuRKBC"
access_token = "928665026-VghhFE4Xxovwv1Sz7Ivizdm6bGjEQn2yFGgd5TIy"
access_token_secret = "xtdeTR1eEkSwlhPwj02OLle64kPFvBUYgfx9FsuaozZdI"

>>>>>>> 977d8880ee9c01cc13bc794c1cbdc7c704068c96
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

count = 0
positive_count = 0
negative_count = 0
neutral_count  = 0
polarity_total = 0
polarity_average = 0
total = 0
def get_sentiment(created_at, tweet_id, username, user_id, favorited, favorite_count, retweeted, retweet_count, followers, following, text):
    global count
    global positive_count
    global negative_count
    global neutral_count
    global polarity_total
    global polarity_average
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
        elif polarity > 0:
            positive_count += 1
            #print("positive_count: {} \n".format(positive_count))
        elif polarity == 0.0:
            neutral_count += 1
            #print("neutral: {} \n".format(neutral_count))
        else:
            print("polarity is undefined \n")

        total = positive_count + negative_count + neutral_count
        polarity_average = (999*polarity_average + polarity) / 1000
        print("Total processed: {}".format(total))
        print("Average sentiment: {}".format(polarity_average))
        print("Positive: {}".format(positive_count))
        print("Negative: {}".format(negative_count))
        print("Neutral: {} \n".format(neutral_count))

    else: 
        #print("the tweet is not in english")
        return

    #http://stackoverflow.com/questions/5729500/how-does-sqlalchemy-handle-unique-constraint-in-table-definition
    timestamp = time.time()
    timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    user = session.query(User).filter_by(user_id=user_id).first()
    if user:
        # insert the new data in db
        tweet_data = Tweet( tweet_id = tweet_id, user_id=user.id, text=text, retweet=retweeted, retweet_count=retweet_count, timestamp=timestamp, sentiment=polarity )
        session.add(tweet_data)
        session.commit()
        #timestamp_existing = session.query(Tweets).filter_by(timestamp=timestamp).one()
        print(username)
    else:
        user_data = User( user_id=user_id, username=username, followers=followers, following=following)
        session.add(user_data)
        session.commit()
        user = session.query(User).filter_by(user_id=user_id).first()
        tweet_data = Tweet( tweet_id=tweet_id, user_id=user.id, text=text, retweet=retweeted, retweet_count=retweet_count,timestamp=timestamp, sentiment=polarity )
        session.add(tweet_data)
        session.commit()
        return
        #print("name exists: {}, time exists: {} \n \n".format(name_existing, timestamp_existing))

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
        print(traceback.format_exc())
        print("sleeping")
        time.sleep(1)
        twitterStream = Stream(auth, listener())
        continue