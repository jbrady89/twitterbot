import datetime, threading, re, time, json, requests, langid, sys, traceback
import tweepy, pymongo
import credentials as config
from pymongo import MongoClient
from tweepy import Stream, OAuthHandler, StreamListener
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

def get_sentiment(tweet):

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
    print("getting sentiment")
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

        
    timestamp = time.time() * 1000
    new_tweet = {
        'tweet_id' : tweet.tweet_id,
        'user_id' : tweet.user_id,
        'username' : tweet.username,
        'created_at' : tweet.created_at,
        'timestamp' : timestamp,
        'sentiment' : polarity,
        'average_sentiment' : polarity_average,
        'text' : text
    }

    #print(tweet)
    # if coordinates:
    #     print(coordinates)
    #     tweet.coordinates = coordinates
		
    # else:
    #     #print(formatted_date)
    #     timestamp = created_at

    # user = posts.find({'user.screen_name' : username}).count()
        
    # timestamp = time.time() * 1000
    # props = {
    #     'timestamp' : timestamp,
    #     'sentiment' : polarity,
    #     'average_sentiment' : polarity_average,
    # }

    # tweet.update(props)

    # # if coordinates:
    # # 	print(coordinates)
    # # 	tweet.coordinates = coordinates
    # print(tweet)

    try:
    	print("saving record")
    	tweets.insert(new_tweet)
    except pymongo.errors.OperationFailure as e:
        print( "Could not connect to server: %s" % e)

def process_data(data):
    global api
    tweet = json.loads(data)

    #print(tweet['text'])
    if 'RT @' in tweet['text']: 
        pass
        # tweet_id = tweet['id']
        # username = tweet['user']['screen_name']
        # followers = tweet['user']['followers_count']
        # following = tweet['user']['friends_count']
        # location = tweet['user']['location']
        # retweeted = tweet['retweeted']
        # retweet_count = tweet['retweet_count']
        # favorited = tweet['favorited']
        # favorite_count = tweet['favorite_count']
        # created_at = tweet['created_at']
        # user_id = tweet['user']['id']
        # text = tweet['text']
        # place = tweet['place']
        #pass
    else:
        tweet = {
            tweet_id : tweet['id'],
            username : tweet['user']['screen_name'],
            user_id :tweet['user']['id'],
            created_at : tweet['created_at'],
            text : tweet['text']
        }
        # if place:
        # 	print(place)
        # 	#place_data = api.geo(place.id)
        # 	#print(place_data)
        # 	#coordinates = place_data.centroid

        #tweet.text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        #print("text: {}".format(tweet.text))
        print("not a rt")
        matches = tweets.find({'text' : tweet.text}).count()
        print(matches)
        if not matches:
            get_sentiment(tweet)

#         tweet_id = tweet['id']
#         username = tweet['user']['screen_name']
#         followers = tweet['user']['followers_count']
#         following = tweet['user']['friends_count']
#         location = tweet['user']['location']
#         print(geolocator.geocode(location))

#         retweeted = tweet['retweeted']
#         retweet_count = tweet['retweet_count']
#         favorited = tweet['favorited']
#         favorite_count = tweet['favorite_count']
#         created_at = tweet['created_at']
#         user_id = tweet['user']['id']
#         text = tweet['text']
#         place = tweet['place']
#         if place:
#         	print(place.id)
#         	coorinates = place.id
#         	#place_data = api.geo_id(place.id)
#         	#print(place_data)
#         	#coordinates = place_data.centroid

#         text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
#         #print("text: {}".format(text))
#         matches = tweets.find({'text' : text}).count()
#         print(matches)
#         if matches:
#             pass
#         else:
#             #print("no matches")
#             get_sentiment(created_at, tweet_id, username, user_id, text)


class listener(StreamListener):

    def on_data(self, data):

        #print(data);
        process_data(data)

    def on_error(self, status):
        print( status.text )

def start_stream(twitterStream, keywords):
    while True:  #Endless loop: personalize to suit your own purposes
        try:
            twitterStream.filter(track=keywords, languages=["en"])

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
            
            "Trump"

        ]

#prevent this function from starting again when fill.py is run
if __name__ == "__main__":
    start_stream(twitterStream, keywords)
