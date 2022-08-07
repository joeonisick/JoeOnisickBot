# This file is a clean slate to test Twitter API related code 
# without mucking with the whole bot

import os
import tweepy
import random
from secrets import declare_secrets
from Support_Functions import send_tweet, send_tweet_reply_with_photo
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

mentions = client.get_users_mentions(id=user_id,expansions='author_id',\
        max_results=100,since_id=since_id)


#*****************************************************************************
#                    PUT THE CODE YOU'RE TESTING HERE
#*****************************************************************************

mentions = client.get_users_mentions(id=user_id,expansions='author_id',\
        max_results=100,since_id=since_id)
print(mentions.data)





#*****************************************************************************
#                STOP PUTTING THE CODE YOU'RE TESTING HERE
#*****************************************************************************

#******------------------------------------------------------------------*****
#           PUT CODE THAT WORKED AND YOU MAY WANT TO REUSE HERE
#******------------------------------------------------------------------*****
"""
#Example code block for writing tweets and multi-line tweets. Multiline uses a .txt file.
#
tweet_text_1 = "You may have noticed that I have major bugs and minimal functionality. Expect more of that. Joe has no idea what he's doing building me, and less than 2-weeks exposure to writing code of any kind. What are you masochists doing here?"
with open('tweet_temp.txt', 'w') as tweet_text_2:
    tweet_text_2.write("Planned Features:\nBug Free Replies!\nFood & Ranch Photo on Request\nIs Joe Still Alive Checks")
client.create_tweet(text=tweet_text_1)
with open('tweet_temp.txt', 'r') as tweet_text_2:
    client.create_tweet(text=tweet_text_2.read())
#
#End code block

#Some test code for a modification of the mentions query if it isn't capturing @'s that aren't mentions
#
query = "@JoeOnisickBot OR to:JoeOnisickBot"
mentions1 = client.get_users_mentions(id=user_id,expansions='author_id',\
         max_results=100,since_id=since_id)
mentions2 = client.search_recent_tweets(query=query, expansions =\
    'author_id', max_results=100, since_id=since_id)

# count=0
# for i in mentions1.data:
#     print("Count: " + str(i))
#     count += 1
count=0
for i in mentions2.data:
    print("Count: " + str(i))
    count += 1
#
#End code block

file, timestamp, picture = retrieve_image(joe_lives_photos)
print("Retrieved %s, from %s, with timestamp %s" % (picture, file, timestamp))

"""