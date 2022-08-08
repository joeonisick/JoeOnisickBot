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

# Call the Tweepy class object
client = tweepy.Client( 
    bearer_token = bearer_token, consumer_key=consumer_key, 
    consumer_secret=consumer_secret, access_token=access_token, 
    access_token_secret=access_token_secret, wait_on_rate_limit= True
) 

def follow_mention(client, user_id, mentions):
    # Follows people that mention the bot if not already following them.
    print("Start follow_mentions.")
    # Create a list of user_ids Joe Bot follows
    following = client.get_users_following(user_id,max_results=1000)
    followed = []

    # Store reponses from follow_responses,txt as a list
    with open('follow_responses.txt', 'r') as responses:
        follow_responses = responses.read().split("\n")
   
    for i in range(0, following.meta['result_count']):
        followed.append(following.data[i].id)

    # Follow mentions if not already following
    list_count = 0 #index var
    #iterate through the returned data and parse mentions
    for user in mentions.includes['users']:
        if (mentions.includes['users'][list_count].id) not in followed:
            if (mentions.includes['users'][list_count].id) != user_id:
                client.follow_user(mentions.includes['users'][list_count].id)
                tweet_id = mentions.data[1].id
                response = random.choice(follow_responses) #choose random response
                tweet_text = ("@%s %s" % (str(mentions.includes['users']\
                    [list_count].username), str(response)))
                client.create_tweet(text=tweet_text, in_reply_to_tweet_id=tweet_id) 
                print(tweet_text)
        list_count += 1
    print("End follow_mentions.")
    return()

def check_mentions(client, user_id):
    print("Start check_mentions.")
    # Retrieve JoeOnisickBot mentions and their author
    # Twitter defines mentions as @user as the first part of the string
    # Using the search function it's possible to pull all @'s within limits

    # Since_id is set to the newest tweet replied to.
    with open('since_id.txt', 'r') as tmp_text:
        since_id = int(tmp_text.read())

    # Retrieves mentions since (since_id) the last run
    mentions = client.get_users_mentions(id=user_id,expansions='author_id',\
         max_results=100,since_id=since_id)
    
    # Return if the query has no results
    if mentions.meta['result_count'] == 0:
        return()

    # Stores the newest tweet ID and rewrites since_id file
    new_since_id = mentions.meta['newest_id']
    with open('since_id.txt', 'w') as temp_txt:
        temp_txt.write(str(since_id))
   
    # Follows the person mentioning the bot
    follow_mention(client, user_id, mentions)
    print("End check_mentions.")
    return(new_since_id)

def retrieve_image(image_type):
    # Pulls infor for an image of the specified type
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
    
    # Set varibles, parsing date/time from file name
    file = str(image_type + "\\" + picture)
    year = picture[0:4]
    month = picture[4:6]
    day = picture[6:8]
    
    # Convert 24 hour time to 12 hour time
    if int(picture[9:11]) > 12:
        hour = str(int(picture[9:11]) - 12)
        period = "PM"
    else:
        hour = picture[9:11]
        period = "AM"
    minute = picture[11:13]
    timestamp = ("%s/%s/%s - %s:%s %s" % \
        (month, day, year, hour, minute, period))

    # Gracefully handle I/O Errors
    try:
        photo = open(file)
        photo.close()
    except IOError:
        print("File not found.")
        return()
    print("End retreive_image.")
    return(file, timestamp, picture)

def check_photo_requests():
    #Checks for supported photo requests
    # Uses a .txt file to simplify passing arguments cleanly
    print("Start check_photo_requests.")
    
    # Photo_since is set to the newest photo sent tweet_id. 
    with open('photo_since.txt', 'r') as tmp_text:
        photo_since = int(tmp_text.read())
    
    with open('photo_query.txt', 'r') as photo_query:
        tweets = client.search_recent_tweets(query=photo_query.read()\
            ,expansions='author_id',max_results=100,since_id=photo_since)
    
    # Return if the query has no results
    if tweets.meta['result_count'] == 0:
        return()

    # Iterate through the retun parse image request
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
        
        # Call retieve_image to select an image and return the detials
        file, timestamp, picture = retrieve_image(image_type)
        
        # Respond accordingly for image type
        if name == "Joe":
            text = ("@%s As of %s Joe was alive. Here's your requested proof of life." % (user, timestamp))
            print(text)
            send_tweet_reply_with_photo(text, file, tweet_id)
        else:
            text = ("@%s Here's the %s photo you requested. It was taken at %s." % (user, name, timestamp))
            print(text)
            send_tweet_reply_with_photo(text, file, tweet_id)

    # Set the since_id to the tweet ID of the latest tweet reply   
    photo_since = tweets.meta['newest_id']
    with open('photo_since.txt', 'w') as tmp_text:
        tmp_text.write(str(photo_since))
    print("End check_photo_requests.")
    return()

def tweet_lyrics():
    # Pulls a random out of context line of lyrics from song_lyrics to tweet
    with open('song_lyrics.txt', 'r') as lyrics:
        song_lyrics = lyrics.read().split("\n")

    # Sets the tweet to random lyrics and calls send_tweet
    tweet_text = random.choice(song_lyrics) #choose random response
    send_tweet(tweet_text)
    print("End tweet_lyrics")
    return()

def stalk_joeonisick():
    #searches for the hashtag #JoeOnisick and retweets it with message
    print("Start stalk_joeonisick")

    # Pulls the tweet ID of the latest joe onisick mention replied to
    with open('stalk_since.txt', 'r') as tmp_text: # Search for the hashtag
        stalk_since = int(tmp_text.read())

    # Search for #JoeOnisick mentions since the last parsed
    tweets = client.search_recent_tweets(query="#JoeOnisick",\
    expansions='author_id',max_results=100,since_id=stalk_since)
    
    # return if the query has no results
    if tweets.meta['result_count'] == 0:
        return()

    # Iterate through return and parse replies
    users = {u["id"]: u for u in tweets.includes['users']}
   
    for tweet in tweets.data:
        if users[tweet.author_id]:
            user = users[tweet.author_id]
            if str(user) != "JoeOnisickBot":
                tweet_id = tweet.id
                
                # Create a quote tweet by building URL using tweet_id
                url =("https://twitter.com/twitter/statuses/" + str(tweet_id))
                tweet_text = ("I see you're talking about Joe. He likes that.")
                quote_tweet(tweet_text, url)
    with open('stalk_since.txt', 'w') as tmp_text: # Search for the hashtag
        tmp_text.write(str(stalk_since))
    print("End stalk_joeonisick")
    return()

def feature_request():
    # Allows users to request features. Building them is not implied.
    print("Start feature_request.")
    
    # Get the ID of the last request responded to.
    with open('feature_since.txt', 'r') as feature_since:
        feature_since = int(feature_since.read())
    
    # Search for 'feature' and 'request' Twitter's API treats a space as and.
    tweets = client.search_recent_tweets(query="@JoeOnisickBot feature request"\
        ,expansions='author_id',max_results=100,since_id=feature_since)
    
    # Build a list of the users that made requests
    users = {u["id"]: u for u in tweets.includes['users']}
    
    # Create a list of response options from the file
    with open('feature_responses.txt', 'r') as responses:
        responses = responses.read().split("\n")
    
    # Iterate through the tweets and parse for require vars
    for tweet in tweets.data:
        if users[tweet.author_id]:
            user = users[tweet.author_id]
            tweet_id = tweet.id
            response = random.choice(responses)
            status = ("@%s %s" % (user, response))
            
            with open('feature_requests.txt', 'a') as requests:
                requests.write(str(tweet.text) + "\n")
            with open('feature_since.txt', 'w') as feature_since:
                feature_since.write(str(tweet_id))
            send_tweet_reply(status, tweet_id)
            print(status)
    print("End feature_request.")
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
            feature_request()
            print("While Loop Count: %s" % count) # Tracking
            if count == 25 or count % 50 == 1500:
                tweet_lyrics() #tweets random song lyrics every ~2 days
            time.sleep(120)
            count += 1
        
        # Handle connectivity issues gracefully with a restart of main()
        except (RemoteDisconnected, ConnectionError, ConnectionAbortedError):
            print("Error handled via retry: RemoteDisconnected, Connection Aborted, or Connection Error.")
            main()

if __name__ == "__main__":
    main()
