import datetime, time, json, langid, sys, traceback
import re
from tweepy import Stream, StreamListener

import follow_bot_db as fb

class listener(StreamListener):

    def on_data(self, data):
        process_data(data)

    def on_error(self, status):
        print( status )

def start_stream(twitterStream):
    while True:  #Endless loop: personalize to suit your own purposes
        try:
            twitterStream.filter(track=[
                                        "stocks",
                                        "daytrades",
                                        "daytrading",
                                        "swing trading",
                                        "options trading",
                                        "futures trading",
                                        "futures",
                                        "forex",
                                        "eur/usd"
                                        "stock trading tutorials"

                                        ], languages=["en"]
                                    )

        except:
            #e = sys.exc_info()[0]  #Get exception info (optional)
            #print ('ERROR:',e ) #Print exception info (optional)
            print(traceback.format_exc())
            print("sleeping")
            #time.sleep(1)
            twitterStream = Stream(fb.auth, listener())
            continue


def process_data(data):
    tweet = json.loads(data)

    #output formatted json to the console
    #print( json.dumps( tweet, sort_keys=True, indent=4, separators=(',', ': ') ) )
    #print(tweet)
    try:
        #tweet = json.loads(data)
        #print(tweet['id'])

        username = tweet['user']['screen_name']
        followers = tweet['user']['followers_count']
        following = tweet['user']['friends_count']
        status_count = tweet['user']['statuses_count']
        description = tweet['user']['description']
        #retweeted = tweet['retweeted']
        #retweet_count = tweet['retweet_count']
        #favorited = tweet['favorited']
        #favorite_count = tweet['favorite_count']
        #created_at = tweet['created_at']
        text = tweet['text']
        user_id = tweet['user']['id']

        #print("136: " , created_at)
        save_user(username, description, user_id, status_count, followers, following, text)
    except:

        print("something went wrong")
        print(traceback.format_exc())
        #print(data)
        #time.sleep(10)

def save_user(username, description, user_id, status_count, followers, following, text):
    
    user = fb.session.query(fb.User).filter_by(user_id=user_id).first()
    #user_data = api.get_user( username )

    # user bio
    #bio = description
    #bio_contains_terms = re.search(r'\bforex\b | \bstocks\b | trade | \btrading\b', bio)
    #print(bio, bio_contains_terms)
    # get their status count
    statuses = status_count

    #only people who have at least 1000+ followers
    #have over 1000 tweets
    #mentioning stocks in their bio/tweets
    #retweets?


    if user:
            print( "user "'{}'" already exists".format(username) )

    else:
        if followers > 1000 and statuses > 1000:
            try:
                timeline = fb.api.user_timeline(username, include_rts=True, count=100)
            except:
                print(traceback.format_exc())
                return

            keyword_occurence = 0
            for tweet in timeline:
                if re.search(r'\bforex\b | \bstock\b | trade | \btrading\b', tweet.text):
                    print("match")
                    keyword_occurence += 1

            if keyword_occurence > 10:
                user_data = fb.User( username=username, followers=followers, following=following, user_id=user_id , tweet=text)
                fb.session.add(user_data)
                fb.session.commit()
                print("user saved")
                keyword_occurence = 0
            else:
                print("not enough keywords")
        else:
            print("criteria not met")

global popular_users
popular_users = []
def get_popular_users(user_group):

    #user_group = session.query(User).all()
    for user in user_group:
        print("Username: ", user.username, "Followers: ", user.followers, "Following: ", user.following, "\n")
        popular_users.append(user.username)

    last_user = len(user_group)


    get_followers(popular_users, followed, unfollowed, last_user)


def unfollow():
    global unfollowed
    followers = fb.api.followers_ids("forexrecap")
    friends = fb.api.friends_ids("forexrecap")

    for f in friends:
        if f not in followers:
            unfollowed += 1
            try:
                fb.api.destroy_friendship(f)
            except:
                print(traceback.format_exc())
                time.sleep(900)

    print("unfollowed this cycle: ", unfollowed)


global followed, unfollower, user_group
followed = 0
unfollowed = 0
import random

def get_followers(popular_users, followed, unfollowed, user_group):

    

    while (followed - unfollowed) != 1000:
        # get the ids of the followers for all the users with more the 1000 followers and following less than 500
        for user in popular_users:
            ids = []
            for page in fb.tweepy.Cursor(fb.api.followers_ids, screen_name=user).pages():
                ids.extend(page)
                time.sleep(10)

            print( len(ids) )
            for user_id in ids:

                if followed < 1000:
                    try: 
                        time.sleep(random.uniform(20,40))
                        fb.api.create_friendship(user_id)
                        
                    except: 
                        print(traceback.format_exc())
                        time.sleep(900)

                    followed += 1
                    print("followed: ", followed)
                else:
                    #give them 5 minutes to follow back
                    time.sleep(300)
                    #reset the followed count
                    print("time to unfollow")
                    unfollow()
                    if unfollowed == 0:
                        print("1000/1000")
                        return 

        last_user = len(user_group)
        # get the group again
        user_group = fb.session.query(fb.User).all()
        user_group = user_group[last_user:]
        get_popular_users()

'''
def unfollow():

    global unfollowed
    unfollowed = 0
    followers = fb.api.followers_ids("forexrecap")
    friends = fb.api.friends_ids("forexrecap")

    for f in friends:
        if f not in followers:
            unfollowed += 1
            print(unfollowed)
            try:
                fb.api.destroy_friendship(f)
            except:
                print(traceback.format_exc())
                time.sleep(900)

    print("unfollowed this cycle: ", unfollowed)
'''
user_group = fb.session.query(fb.User).all()
twitterStream = Stream(fb.auth, listener())

import threading

def start(twitterStream, user_group):
    #t1 = threading.Thread(target=start_stream(twitterStream))
    # Make threads daemonic, i.e. terminate them when main thread
    # terminates. From: http://stackoverflow.com/a/3788243/145400
    #t1.daemon = True
    
    start_stream(twitterStream)
    #get_popular_users(user_group)

start(twitterStream,user_group)
#for thread in start(twitterStream, user_group):
    #thread.join()

#unfollow()
