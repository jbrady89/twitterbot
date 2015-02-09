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

consumer_key = "rY3Q4lLIAcLRXPm66JoU2jL8X"
consumer_secret = "xkTrpkamaiDQaiAdEvcvJLj6hmaLH0DL2m5bE4l4H7ROFuRKBC"
access_token = "928665026-VghhFE4Xxovwv1Sz7Ivizdm6bGjEQn2yFGgd5TIy"
access_token_secret = "xtdeTR1eEkSwlhPwj02OLle64kPFvBUYgfx9FsuaozZdI"
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

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
            user = session.query(User).filter_by(user_id=user_id).first()
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

# call this to fill in missing tweets if program goes stalls/goes offline

def fill_in_missing():
    old_tweets                      =   []
    last_ids                        =   []
    MAX_ATTEMPTS                    =   10000
    COUNT_OF_TWEETS_TO_BE_FETCHED   =   50000
    count = 0
    for i in range(0, MAX_ATTEMPTS):

        if(COUNT_OF_TWEETS_TO_BE_FETCHED < len(old_tweets)):
            break # we reached our goal

        #----------------------------------------------------------------#
        # STEP 1: Query Twitter
        # STEP 2: Save the returned tweets
        # STEP 3: Get the next max_id
        #----------------------------------------------------------------#

        # STEP 1: Query Twitter
        if(0 == i):
            # get the last tweet_id from Tweet table

            last_tweet = session.query(Tweet).order_by(Tweet.id.desc()).first()
            last_tweet_id = last_tweet.tweet_id
            print("last tweet_id", last_tweet_id, "\n")

            try:

                results = api.search(q="apple", lang="en", count='100', since_id= last_tweet_id )
                #to see the structure of a single status uncomment this
                #print(results[0])

            except:
                # rate limit exceeded
                print("fook")
                print(traceback.format_exc())
                time.sleep(900)
                continue

        else:
            print("next page")
            # After the first call we should have max_id from result of previous call. Pass it in query.
            try:
                results = api.search(q="apple", lang="en", count='100', since_id=last_tweet_id , max_id=next_max_id)
            except:
                # rate limit exceeded
                print("fook")
                time.sleep(900)
                continue

        # STEP 2: Save the returned tweets

        for result in results:


            text           = result.text
            tweet_id       = result.id
            author         = result.author
            user_id        = author.id
            username       = author.screen_name
            following      = author.friends_count
            followers      = author.followers_count
            retweeted      = result.retweeted
            retweet_count  = result.retweet_count
            favorited      = result.favorited
            favorite_count = result.favorite_count
            created_at     = result.created_at

            result  =   {

                            "text": text,
                            "tweet_id": tweet_id,
                            "author": {
                                "username": username,
                                "id": user_id,
                                "following": following,
                                "followers": followers,
                                "retweeted": retweeted,
                                "retweet_count": retweet_count,
                                "favorited": favorited,
                                "favorite_count": favorite_count
                            },
                            # need to format this
                            "created_at": created_at

                        }

            old_tweets.append(result)

            print(result["created_at"])
            print(len(old_tweets))



        # STEP 3: Get the next max_id
        try:
            # Parse the data returned to get max_id to be passed in next call.
            next_max_id = results[-1].id
            created_at = results[-1].created_at

            #track ids to make sure they are different
            last_ids.append(next_max_id)
        except:
            # No more next pages
            print("no more pages")

            #reverse the old_tweet array so the oldest one can be inserted into the db first
            old_tweets = old_tweets[::-1]
            #pass iterate through old tweets and pass the data to the sentiment function
            break


class listener(StreamListener):

    def on_data(self, data):
        process_data(data)

    def on_error(self, status):
        print( status.text )

fill_in_missing()

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
        print(traceback.format_exc())
        print("sleeping")
        time.sleep(1)
        twitterStream = Stream(auth, listener())
        continue
'''
