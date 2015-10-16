import tweepy, pymongo, config
from tweepy import Stream, OAuthHandler, StreamListener

consumer_key = config.key
consumer_secret = config.secret 
access_token = config.token
access_token_secret = config.token_secret
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

geo_data = api.geo_id('8173485c72e78ca5');
centroid = geo_data.centroid
print(centroid[0], centroid[1])
reverse_geo = api.reverse_geocode(centroid[0], centroid[1])
print(reverse_geo)