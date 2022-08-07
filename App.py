#Never gonna give you up 
from http.client import HTTPSConnection, RemoteDisconnected
from socket import socket
import tweepy
import random
import os
import time
from secrets import declare_secrets

from urllib3 import HTTPSConnectionPool
from Support_Functions import get_user, send_tweet, \
    send_tweet_reply_with_photo, send_tweet_reply, quote_tweet

#Twitter rate limt reference: 
#https://developer.twitter.com/en/docs/twitter-api/rate-limits

#Configure the client for use of OAuth1.0 and OAuth2.0 (API object dependant)
#https://developer.twitter.com/en/docs/authentication/guides/v2-authentication-mapping

#provide keys and file locations
bearer_token, consumer_key,consumer_secret,access_token,access_token_secret, \
    ranch_photos, joe_lives_photos, cow_photos, food_photos, dog_photos \
        = declare_secrets() #defines secret & API keys & file folders

client = tweepy.Client( 
    bearer_token = bearer_token, consumer_key=consumer_key, 
    consumer_secret=consumer_secret, access_token=access_token, 
    access_token_secret=access_token_secret, wait_on_rate_limit= True
) 

def follow_mention(client, user_id, mentions):
    print("Start follow_mentions.")
    #create a list of user_ids Joe Bot follows
    following = client.get_users_following(user_id,max_results=1000)
    followed = []

    # Store reponses from follow_responses,txt as a list
    with open('follow_responses.txt', 'r') as responses:
        follow_responses = responses.read().split("\n")
   
    for i in range(0, following.meta['result_count']):
        followed.append(following.data[i].id)

    #Follow mentions if not already following
    list_count = 0 #index var
    for user in mentions.includes['users']:
        if (mentions.includes['users'][list_count].id) not in followed:
            if (mentions.includes['users'][list_count].id) != user_id:
                client.follow_user(mentions.includes['users'][list_count].id)
                tweet_id = mentions.data[1].id
                response = random.choice(follow_responses) #choose random response
                tweet_text = ("@%s %s" % (str(mentions.includes['users'][list_count].username), str(response)))
                client.create_tweet(text=tweet_text, in_reply_to_tweet_id=tweet_id) 
                print(tweet_text)
        list_count += 1
    print("End follow_mentions.")
    return()

def check_mentions(client, user_id):
    print("Start check_mentions.")
    # Retrieve JoeOnisickBot mentions and their author
    # Twitter defines mentions as @user as the first part of the string

    # Since_id is set to the newest tweet replied to.
    with open('since_id.txt', 'r') as tmp_text:
        since_id = int(tmp_text.read())

    mentions = client.get_users_mentions(id=user_id,expansions='author_id',\
         max_results=100,since_id=since_id)
    if mentions.meta['result_count'] == 0:
        return()

    new_since_id = mentions.meta['newest_id']
    with open('since_id.txt', 'w') as temp_txt:
        temp_txt.write(str(since_id))
    follow_mention(client, user_id, mentions)
    print("End check_mentions.")
    return(new_since_id)

def retrieve_image(image_type):
    print("Start retreive_image.")
    # supported image_types are: 
    # ranch, joe_lives_photos, cow_photos, food_photos, dog_photos
    image_list = []

    #for joe_lives_photos pull the latest, else pull random
    if image_type == joe_lives_photos:
        for file in os.listdir(image_type):
            if file.endswith(".jpg"):
                image_list.append(file)
        image_list.sort(reverse=True)
        picture = image_list[0]
    else:
        for file in os.listdir(image_type):
            if file.endswith(".jpg"):
                image_list.append(file)
                picture = random.choice(image_list)
    file = str(image_type + "\\" + picture)
    year = picture[0:4]
    month = picture[4:6]
    day = picture[6:8]
    if int(picture[9:11]) > 12:
        hour = str(int(picture[9:11]) - 12)
        period = "PM"
    else:
        hour = picture[9:11]
        period = "AM"
    minute = picture[11:13]
    timestamp = ("%s/%s/%s - %s:%s %s" % \
        (month, day, year, hour, minute, period))

    try:
        photo = open(file)
        photo.close()
    except IOError:
        print("File not found.")
    print("End retreive_image.")
    return(file, timestamp, picture)

def check_photo_requests():
    # Uses a .txt file to simplify passing arguments cleanly
    print("Start check_photo_requests.")
    # Photo_since is set to the newest photo sent tweet_id. 
    with open('photo_since.txt', 'r') as tmp_text:
        photo_since = int(tmp_text.read())
    
    with open('photo_query.txt', 'r') as photo_query:
        tweets = client.search_recent_tweets(query=photo_query.read()\
            ,expansions='author_id',max_results=100,since_id=photo_since)
    if tweets.meta['result_count'] == 0:
        return()

    users = {u["id"]: u for u in tweets.includes['users']}
    for tweet in tweets.data:
        if users[tweet.author_id]:
            user = users[tweet.author_id]
            tweet_id = tweet.id
            if "joe" and "alive" in tweet.text.lower(): 
                image_type = joe_lives_photos
                name = "Joe"
            elif "send" and "cow" in tweet.text.lower(): 
                image_type = cow_photos
                name = "cow"
            elif "send" and "food" in tweet.text.lower(): 
                image_type = food_photos
                name = "food"
            elif "send" and "ranch" in tweet.text.lower(): 
                image_type = ranch_photos
                name = "ranch"
            elif "send" and "dog" in tweet.text.lower():
                image_type = dog_photos
                name = "dog"
            else:
                print("A returned tweet did not match. This is a bug.")
                return()
        file, timestamp, picture = retrieve_image(image_type)
        if name == "Joe":
            text = ("@%s As of %s Joe was alive. Here's your requested proof of life." % (user, timestamp))
            print(text)
            send_tweet_reply_with_photo(text, file, tweet_id)
        else:
            text = ("@%s Here's the %s photo you requested. It was taken at %s." % (user, name, timestamp))
            print(text)
            send_tweet_reply_with_photo(text, file, tweet_id)
    
    photo_since = tweets.meta['newest_id']
    with open('photo_since.txt', 'w') as tmp_text:
        tmp_text.write(str(photo_since))
    print("End check_photo_requests.")
    return()

def tweet_lyrics():
    # Pulls a random out of context line of lyrics from song_lyrics to tweet
    with open('song_lyrics.txt', 'r') as lyrics:
        song_lyrics = lyrics.read().split("\n")

    tweet_text = random.choice(song_lyrics) #choose random response
    send_tweet(tweet_text)

def stalk_joeonisick():
    #searches for the hashtag #JoeOnisick and retweets it with message
    with open('since_id.txt', 'r') as tmp_text: # Search for the hashtag
        since_id = tmp_text.read()

    tweets = client.search_recent_tweets(query="#JoeOnisick",\
    expansions='author_id',max_results=100,since_id=since_id)
    
    users = {u["id"]: u for u in tweets.includes['users']}
    for tweet in tweets.data:
        if users[tweet.author_id]:
            user = users[tweet.author_id]
            if str(user) != "JoeOnisickBot":
                tweet_id = tweet.id
                url =("https://twitter.com/twitter/statuses/" + str(tweet_id))
                tweet_text = ("I see you're talking about Joe. He likes that.")
                quote_tweet(tweet_text, url)
    
    return()

def main():
    print("Start main.")
    user_id = 1554986957532438535 #set JoeOnisickBot's user id

    count = 1
    while True:
        try:  
            stalk_joeonisick()
            check_mentions(client, user_id)
            check_photo_requests()
            print("While Loop Count: %s" % count)
            if count == 5 or count % 45 == 0:
                tweet_lyrics() #tweets random song lyrics every ~90 minutes
            time.sleep(120)
            count += 1
        except (RemoteDisconnected, ConnectionError, ConnectionAbortedError):
            print("Error handled via retry: RemoteDisconnected, Connection Aborted, or Connection Error.")
            main()

if __name__ == "__main__":
    main()
