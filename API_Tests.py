# This file is a clean slate to test Twitter API related code 
# without mucking with the whole bot

import os
import tweepy
import random
from secrets import declare_secrets
from Support_Functions import send_tweet, send_tweet_reply_with_photo, send_tweet_reply, get_user
from App import retrieve_image

#provide keys and file locations
bearer_token, consumer_key,consumer_secret,access_token,access_token_secret, \
    ranch_photos, joe_lives_photos, cow_photos, food_photos, dog_photos \
        = declare_secrets() #defines secret & API keys & file folders

client = tweepy.Client( 
    bearer_token = bearer_token, consumer_key=consumer_key, 
    consumer_secret=consumer_secret, access_token=access_token, 
    access_token_secret=access_token_secret, wait_on_rate_limit= True
) 

#common bot variables
user_id = 1554986957532438535 #set JoeOnisickBot's user id

with open('since_id.txt', 'r') as since_id:
    since_id = since_id.read()
# photo_since is set to the oldest photo sent. Since ID is used inclusively.
with open('photo_since.txt', 'r') as photo_since:
    photo_since = photo_since.read()

def get_mentions(user_id):
    mentions = client.get_users_mentions(id=user_id,expansions='author_id',\
            max_results=100, since_id=1556257587070488575, until_id=1556257587070488577)
    return(mentions)


#*****************************************************************************
#                    PUT THE CODE YOU'RE TESTING HERE
#*****************************************************************************







#*****************************************************************************
#                STOP PUTTING THE CODE YOU'RE TESTING HERE
#*****************************************************************************
#*****************************************************************************
#            USE THIS CODE BLOCK TO TEST TWITTER QUERIES.
# SAVE THE TEST QUERY IN A FILE CALLED TEST_QUERY TO SIMPLIFY STRING PASSING
#*****************************************************************************
since_id = 1554598110957125634 # Tweet_id to set how far back to search

def search_tweets(since_id):
    with open('test_query.txt', 'r') as test_query: # This is your query code
        tweets = client.search_recent_tweets(query=test_query.read()\
            ,expansions='author_id',max_results=100,since_id=since_id)
    return(tweets)

# Insert test code below




#*****************************************************************************
#                STOP PUTTING THE CODE YOU'RE TESTING HERE
#*****************************************************************************
#******------------------------------------------------------------------*****
#           PUT CODE THAT WORKED AND YOU MAY WANT TO REUSE HERE
#******------------------------------------------------------------------*****