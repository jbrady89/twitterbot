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
import stream

def process_old_tweets(old_tweets):
    print("processing old tweets")
    for tweet in old_tweets:
        print(tweet)
        stream.get_sentiment(
                        tweet["created_at"],
                        tweet["tweet_id"],
                        tweet["author"]["username"],
                        tweet["author"]["id"],
                        tweet["author"]["favorited"],
                        tweet["author"]["favorite_count"],
                        tweet["author"]["retweeted"],
                        tweet["author"]["retweet_count"],
                        tweet["author"]["followers"],
                        tweet["author"]["following"],
                        tweet["text"]
                    )

def fill_in_missing():
    old_tweets                      =   []
    last_ids                        =   []
    MAX_ATTEMPTS                    =   10000
    COUNT_OF_TWEETS_TO_BE_FETCHED   =   50000
    count = 0
    while True:

        #----------------------------------------------------------------#
        # STEP 1: Query Twitter
        # STEP 2: Save the returned tweets
        # STEP 3: Get the next max_id
        #----------------------------------------------------------------#

        # STEP 1: Query Twitter
        if(count == 0):
            # get the last tweet_id from Tweet table

            last_tweet = stream.session.query(Tweet).order_by(Tweet.id.desc()).first()
            last_tweet_id = last_tweet.tweet_id
            print("last tweet_id", last_tweet_id, "\n")

            try:

                results = api.search(q="Apple OR aapl OR iphone OR ipad OR ipod OR imac OR macbook", lang="en", count='100', since_id= last_tweet_id )
                #to see the structure of a single status uncomment this
                #print(results[0])

            except:
                # rate limit exceeded
                print("fook")
                print(traceback.format_exc())
                time.sleep(900)
                continue

            count += 1

        else:
            print("next page")
            # After the first call we should have max_id from result of previous call. Pass it in query.
            try:
                results = api.search(q="Apple OR aapl OR iphone OR ipad OR ipod OR imac OR macbook", lang="en", count='100', since_id=last_tweet_id , max_id=next_max_id)
            except:
                # rate limit exceeded
                print("fook")
                time.sleep(900)
                continue

        # STEP 2: Save the returned tweets

        for result in results:

            text            = result.text
            tweet_id        = result.id
            author          = result.author
            user_id         = author.id
            username        = author.screen_name
            following       = author.friends_count
            followers       = author.followers_count
            retweeted       = result.retweeted
            retweet_count   = result.retweet_count
            favorited       = result.favorited
            favorite_count  = result.favorite_count
            created_at      = result.created_at
            time_in_seconds = created_at.timestamp()
            adjust_to_EST   = time_in_seconds - 18000
            timestamp       = datetime.datetime.fromtimestamp(adjust_to_EST).strftime('%Y-%m-%d %H:%M:%S')
            result          =   {
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
                                    "created_at": timestamp
                                }

            old_tweets.append(result)

            print(result["created_at"])
            print(len(old_tweets))

        # STEP 3: Get the next max_id
        try:

            # Parse the data returned to get max_id to be passed in next call.
            next_max_id = results[-1].id

            #track ids to make sure they are different
            #last_ids.append(next_max_id)
        except:

            # No more next pages
            print("no more pages")

            #reverse the old_tweet array so the oldest one can be inserted into the db first
            old_tweets = old_tweets[::-1]

            #iterate through old tweets and pass the data to the sentiment function
            process_old_tweets(old_tweets)
            break

consumer_key = "rY3Q4lLIAcLRXPm66JoU2jL8X"
consumer_secret = "xkTrpkamaiDQaiAdEvcvJLj6hmaLH0DL2m5bE4l4H7ROFuRKBC"
access_token = "928665026-VghhFE4Xxovwv1Sz7Ivizdm6bGjEQn2yFGgd5TIy"
access_token_secret = "xtdeTR1eEkSwlhPwj02OLle64kPFvBUYgfx9FsuaozZdI"
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

fill_in_missing()
