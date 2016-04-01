import datetime, threading, re, time, json, requests, langid, sys, traceback
import tweepy, pymongo
import credentials as config
import Queue
#from geopy.geocoders import Nominatim
from tweepy import Stream, OAuthHandler, StreamListener
from textblob import TextBlob
from pymongo import MongoClient
from threading import Thread

consumer_key = config.key
consumer_secret = config.secret 
access_token = config.token
access_token_secret = config.token_secret
tweet_queue = Queue.Queue(maxsize=0)

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

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

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

def get_sentiment(tweet):
    print("getting sentiment")
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

    print("the tweet", tweet)

    #time.sleep(5)

    timestamp = datetime.datetime.now()
    classify = langid.classify(tweet['text']);
    lang = classify[0]

    # print("getting sentiment for tweet: {}".format(tweet))

    if lang == "en":
        processed_text = TextBlob(tweet['text'])
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

    else:
        print("the tweet is not in english")
        return

    # # in order to get EST
    # #check the format and adjust accordingly
    if isTimeFormat(tweet['created_at']):

        formatted_date = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
        #http://stackoverflow.com/questions/9637838/convert-string-date-to-timestamp-in-python
        date_in_seconds = time.mktime(datetime.datetime.strptime(formatted_date, "%Y-%m-%d %H:%M:%S").timetuple())
        # subtract 5 hours from UTC to get EST
        adjusted_time = int(date_in_seconds) - 18000
        timestamp = datetime.datetime.fromtimestamp(adjusted_time).strftime('%Y-%m-%d %H:%M:%S')

    else:
        timestamp = created_at
        
    timestamp = time.time() * 1000
    props = {
        'timestamp' : timestamp,
        'sentiment' : polarity,
        'average_sentiment' : polarity_average,
    }

    tweet.update(props)

    # # if coordinates:
    # # 	print(coordinates)
    # # 	tweet.coordinates = coordinates
    # print(tweet)

    try:
    	print("saving record")
    	tweets.insert(tweet)
    except pymongo.errors.OperationFailure as e:
        print( "Could not connect to server: %s" % e)

def process_data(data):

    tweet = json.loads(data)
    if tweet.get('text'):
        if 'RT @' in tweet['text']: 
            pass
        else:
            newTweet = {
                "tweet_id" : tweet['id'],
                "username" : tweet['user']['screen_name'],
                "user_id" :tweet['user']['id'],
                "created_at": tweet['created_at'],
                "text" : tweet['text']
            }
            # TODO: add location to the saved properties
            # if place:
            # 	print(place)
            # 	#place_data = api.geo(place.id)
            # 	#print(place_data)
            # 	#coordinates = place_data.centroid

            #tweet.text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
            #print("text: {}".format(tweet.text))
            print("not a rt")
            print(newTweet['text'])
            try:
                matches = tweets.find({'text' : newTweet['text']}).count()
            except: 
                e = sys.exc_info()[0]  #Get exception info (optional)
                print ('ERROR:',e ) #Print exception info (optional)

            if not matches:
                get_sentiment(newTweet)

class listener(StreamListener):

    def on_data(self, data):

        #tweet = json.loads(data)
        tweet_queue.put(data)            

    def on_error(self, status):
        print( status.text )

# def start_stream(twitterStream, keywords):
#     while True:
#         print("starting stream...")
#         try:
#             twitterStream.filter(track=keywords, languages=["en"])

#         except:
#             e = sys.exc_info()[0]  #Get exception info (optional)
#             print ('ERROR:',e ) #Print exception info (optional)
#             #print(traceback.format_exc())
#             twitterStream = Stream(auth, listener())
#             continue

def process_tweet_queue(tweet_queue):
    while True:
        tweet = tweet_queue.get()
        process_data(tweet)
        tweet_queue.task_done()
   
keywords = [
            
            "Trump"

        ]

tweet_processor = Thread(target=process_tweet_queue, args=(tweet_queue,))
tweet_processor.setDaemon(True)
tweet_processor.start()

twitterStream = Stream(auth, listener())
twitterStream.filter(track=keywords)
