import datetime, threading, re, time, json, requests, langid, sys, traceback
import tweepy, pymongo
import credentials as config
from pymongo import MongoClient
#from geopy.geocoders import Nominatim
from tweepy import Stream, OAuthHandler, StreamListener
#import twitter
# from sqlalchemy import create_engine, Column, Integer, Float, Text, Boolean
# from sqlalchemy import DateTime
# from sqlalchemy import or_
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy_declarative import Tweet, User, Price
from textblob import TextBlob

consumer_key = config.key
consumer_secret = config.secret 
access_token = config.token
access_token_secret = config.token_secret
# tapi = twitter.API(consumer_key=consumer_key, 
# 		consumer_secret=consumer_secret, 
# 		access_token_key=access_token, 
# 		access_token_secret=access_token_secret)

# print(tapi.verifyCredenials())
#r = Twitter.request('geo/id/%s' % '27c45d804c777999.json')
#data = r.json()
#print(data)

db_user = sys.argv[1]
db_pass = sys.argv[2]
print(db_user,db_pass)
client = MongoClient('mongodb://{}:{}@ds051893.mongolab.com/geostream'.format(db_user, db_pass), 51893)
db = client.geostream
print(db)
posts = db.posts
tweets = db.tweets

global session
global auth
global api

count = 0
positive_count = 0
negative_count = 0
neutral_count  = 0
polarity_total = 0
cursor = tweets.find().sort( '_id' , pymongo.DESCENDING ).limit(1);
for document in cursor:
    print(document)
    polarity_average = document['average_sentiment']
positive_polarity_average = 0
negative_polarity_average = 0
total = 0

def Tweet( object ):
    pass

def isTimeFormat(input):
    try:
        time.strptime(input, '%a %b %d %H:%M:%S +0000 %Y')

        return True
    except ValueError:

        return False

def get_sentiment(created_at, tweet_id, username, user_id, favorited, favorite_count, retweeted, retweet_count, followers, following, text, coordinates):
    global count
    global positive_count
    global negative_count
    global neutral_count
    global polarity_total
    global polarity_average
    global positive_polarity_average
    global negative_polarity_average
    global polarity
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

        # print("Total processed: {}".format(total))
        # print("Average positive sentiment: {}".format(positive_polarity_average))
        # print("Average negative sentiment: {}".format(negative_polarity_average))
        # print("Polarity: {}".format(polarity))
        # print("Average sentiment: {}".format(polarity_average))
        # print("Positive: {}".format(positive_count))
        # print("Negative: {}".format(negative_count))
        # print("Neutral: {} \n".format(neutral_count))

    else:
        print("the tweet is not in english")
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

    user = posts.find({'user.screen_name' : username}).count()
        
    timestamp = time.time() * 1000
    tweet = {
        'tweet_id' : tweet_id,
        'user_id' : user_id,
        'username' : username,
        'created_at' : created_at,
        'timestamp' : timestamp,
        'sentiment' : polarity,
        'average_sentiment' : polarity_average,
        'text' : text
    }

    # if coordinates:
    # 	print(coordinates)
    # 	tweet.coordinates = coordinates


    try:
    	print("saving record")
    	tweets.insert(tweet)
    except pymongo.errors.OperationFailure as e:
        print( "Could not connect to server: %s" % e)

def process_data(data):
    tweet = json.loads(data)

    if 'RT' not in tweet['text'].upper(): 
        #print(tweet['coordinates'])
        tweet_id = tweet['id']
        username = tweet['user']['screen_name']
        followers = tweet['user']['followers_count']
        following = tweet['user']['friends_count']
        location = tweet['user']['location']
        retweeted = tweet['retweeted']
        retweet_count = tweet['retweet_count']
        favorited = tweet['favorited']
        favorite_count = tweet['favorite_count']
        created_at = tweet['created_at']
        user_id = tweet['user']['id']
        text = tweet['text']
        place = tweet['place']
        # if place:
        # 	print(place)
        # 	#place_data = api.geo(place.id)
        # 	#print(place_data)
        # 	#coordinates = place_data.centroid

        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        print("text: {}".format(text))

        matches = tweets.find({'text' : text}).count()
        #print(matches)

        if matches:
            pass
        else:
            print("no matches")
            get_sentiment(created_at, tweet_id, username, user_id, favorited, favorite_count, retweeted, retweet_count, followers, following, coordinates=None)


class listener(StreamListener):

    def on_data(self, data):

        print(data);
        process_data(data)

    def on_error(self, status):
        print( status.text )

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
print(auth)
auth.set_access_token(access_token, access_token_secret)
twitterStream = Stream(auth, listener())
print(twitterStream)
api = tweepy.API(auth)

keywords = [
            
            "trump"

        ]

#prevent this function from starting again when fill.py is run
if __name__ == "__main__":
    start_stream(twitterStream, keywords)
