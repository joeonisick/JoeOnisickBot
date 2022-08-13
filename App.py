#Never gonna give you up 
from http.client import RemoteDisconnected
import tweepy # Twitter API access module
import random # Random Choices
import os # File access
import time # wait, etc.
import pickle # Read/Write binary files to persistently store vars
from secrets import declare_secrets
from Support_Functions import get_hashtag, get_tweets, read_since_id, \
    write_since_id, print_tweets, send_tweet, quote_tweet, send_tweet_reply,\
        send_tweet_reply_with_photo, retrieve_next_image

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

def get_tweet_data():
    # Sets the since_id to the tweet ID of the last request
    since_id = read_since_id('notifications')

    # Pull the tweet data to process. Pulls notifications and the #JoeOnisick tag
    notifications = get_tweets(since_id)
    onisick_tag = get_hashtag("#JoeOnisick", since_id)

    # Write the new latest since_id to persistent storage
    if notifications.meta['result_count'] == 0: # Check for no results
        notification_since = int(0)
    else:
        notification_since = int(notifications.meta['newest_id'])

    if onisick_tag.meta['result_count'] == 0: # Check for no results
        onisick_tag_since = int(0)
    else:
        onisick_tag_since = int(onisick_tag.meta['newest_id'])

    # Find the newest tweet ID
    if notification_since > onisick_tag_since:
        # Writes the new_since_id to persistent storage    
        write_since_id(notification_since ,'notifications')
    elif onisick_tag_since > notification_since:
        write_since_id(onisick_tag_since ,'notifications')
    elif notification_since == onisick_tag_since and notification_since !=0:
        write_since_id(notification_since ,'notifications')
    elif notification_since == 0 and onisick_tag_since == 0:
        print('No New Results')
    else:
        print("Bug found in get_twitter_data.") # Should not else here.

    print("End get_tweet_data")
    return(notifications, onisick_tag)

def process_onisick_tag(onisick_tag):
    # Quote tweets mentions of #JoeOnisick
    print("Start process_onisick_tag")

    # Return if the query has no results
    if onisick_tag.meta['result_count'] == 0:
        print("No Results. End process_onisick_tag")
        return()

    # Build a list of user info for returned tweets
    users = {u["id"]: u for u in onisick_tag.includes['users']}
   
    for tweet in onisick_tag.data: # Iterate through returned tweets
        if users[tweet.author_id]: # Match users to author_id
            user = users[tweet.author_id] # Store the username
            if str(user) != "JoeOnisickBot": # Ensure it's not a self tweet
                tweet_id = tweet.id # Store the tweet id
                
                # Create a quote tweet by building URL using tweet_id
                url =("https://twitter.com/twitter/statuses/" + str(tweet_id))
                tweet_text = ("I see you're talking about Joe. He likes that.")
                print(tweet_text, url)
                quote_tweet(tweet_text, url)

    print("End process_onisick_tag")
    return()

def user_help(notifications):
    # Searches for JoeOnisickBot mentions including 'help' and replies
    print("Start user_help.")

    # Return if the query has no results
    if notifications.meta['result_count'] == 0:
        print("No Results. End user_help")
        return()

    with open('/perm_objects/Interactions.txt', 'r') as tmp_text:
        tweet_text = tmp_text.read()

    # Build a users list of help requests
    users = {u["id"]: u for u in notifications.includes['users']}
   
    for tweet in notifications.data:
        if users[tweet.author_id]:
            user = users[tweet.author_id]
            tweet_id = tweet.id
            if "help" in tweet.text.lower() and "options" in tweet.text.lower():
                status = ("@%s %s" % (user, tweet_text))
                print(status + " : " + str(tweet_id))
                send_tweet_reply(status, tweet_id)
    
    print("End user_help.")
    return()

def feature_request(notifications):
    # Allows users to request features. Actually implementing them is not implied.
    print("Start feature_request.")
         
    # Return if the query has no results
    if notifications.meta['result_count'] == 0:
        print("No Results. End feature_request")
        return()
    
    # Build a list of the users that made requests
    users = {u["id"]: u for u in notifications.includes['users']}
    
    # Create a list of response options from the file
    with open('/Response_Options/feature_responses.txt', 'r') as responses:
        responses = responses.read().split("\n")
    
    # Iterate through the tweets and parse for required vars
    for tweet in notifications.data:
        if users[tweet.author_id]:
            user = users[tweet.author_id]
            tweet_id = tweet.id
            if "feature" in tweet.text.lower() and "request" in tweet.text.lower():  
                response = random.choice(responses)
                status = ("@%s %s" % (user, response))
                with open('perm_objects/feature_requests.txt', 'a') as requests:
                    requests.write(str(tweet.text) + "\n")

                print(status + ":" + str(tweet_id))
                send_tweet_reply(status, tweet_id)
   
    print("End feature_request.")
    return()

def check_photo_requests(notifications):
    #Checks for supported photo requests
    print("Start check_photo_requests.")
       
    # Return if the query has no results
    if notifications.meta['result_count'] == 0:
        print("No Results. End check_photo_requests")
        return()

    # Build a users list of tweets
    users = {u["id"]: u for u in notifications.includes['users']}
    
    # Iterate through tweets
    for tweet in notifications.data:
        if users[tweet.author_id]:
            user = users[tweet.author_id]
            tweet_id = tweet.id

            if "joe" in tweet.text.lower() and "alive" in tweet.text.lower(): 
                image_type = joe_lives_photos
                name = "Joe"
                # Call retieve_next_image to select an image and return the detials
                file, timestamp = retrieve_next_image(image_type)
                text = ("@%s As of %s Joe was alive. Here's your requested proof of life." % (user, timestamp))
                
                print("%s:%s:%s" % (text, file, tweet_id))                    
                send_tweet_reply_with_photo(text, file, tweet_id)
            if "send" in tweet.text.lower() and "cow" in tweet.text.lower(): 
                image_type = cow_photos
                name = "cow"
                # Call retieve_next_image to select an image and return the detials
                file, timestamp = retrieve_next_image(image_type)
                text = ("@%s Here's the %s photo you requested. It was taken at %s." % (user, name, timestamp))
                
                print("%s:%s:%s" % (text, file, tweet_id))                    
                send_tweet_reply_with_photo(text, file, tweet_id)           
            if "send" in tweet.text.lower() and "food" in tweet.text.lower(): 
                image_type = food_photos
                name = "food"
                # Call retieve_image to select an image and return the detials
                file, timestamp = retrieve_next_image(image_type)
                text = ("@%s Here's the %s photo you requested. It was taken at %s." % (user, name, timestamp))

                print("%s:%s:%s" % (text, file, tweet_id))                    
                send_tweet_reply_with_photo(text, file, tweet_id)           
            if "send" in tweet.text.lower() and "ranch" in tweet.text.lower(): 
                image_type = ranch_photos
                name = "ranch"
                # Call retieve_image to select an image and return the detials
                file, timestamp = retrieve_next_image(image_type)
                text = ("@%s Here's the %s photo you requested. It was taken at %s." % (user, name, timestamp))
                
                print("%s:%s:%s" % (text, file, tweet_id))                    
                send_tweet_reply_with_photo(text, file, tweet_id)           
            if "send" in tweet.text.lower() and "dog" in tweet.text.lower():
                image_type = dog_photos
                name = "dog"
                # Call retieve_image to select an image and return the detials
                file, timestamp = retrieve_next_image(image_type)
                text = ("@%s Here's the %s photo you requested. It was taken at %s." % (user, name, timestamp))
                
                print("%s:%s:%s" % (text, file, tweet_id))                    
                send_tweet_reply_with_photo(text, file, tweet_id)           

    print("End check_photo_requests.")
    return()

def follow_mention(notifications):
    # Follows people that mention the bot if not already following them.
    print("Start follow_mentions.")

    # Return if the query has no results
    if notifications.meta['result_count'] == 0:
        print("No Results. End follow_mentions")
        return()

    # Iterate through users
    for user in notifications.includes['users']:
        client.follow_user(user.id)

    print("End follow_mentions.")
    return()

def tweet_lyrics():
    # Pulls a random out of context line of lyrics from song_lyrics to tweet
    with open('/perm_objects/song_lyrics.txt', 'r') as lyrics:
        song_lyrics = lyrics.read().split("\n")

    # Sets the tweet to random lyrics and calls send_tweet
    tweet_text = random.choice(song_lyrics) #choose random response
    send_tweet(tweet_text)
    print("End tweet_lyrics")
    return()

def main():
    print("Start main.")
    # user_id = 1554986957532438535 #set JoeOnisickBot's user id

    count = 1
    while True:
        try:  
            notifications, onisick_tag = get_tweet_data()
            print_tweets(notifications)
            user_help(notifications)
            process_onisick_tag(onisick_tag)
            feature_request(notifications)
            check_photo_requests(notifications)
            follow_mention(notifications)
            print("While Loop Count: %s" % count) # Tracking
            if count % 3000 == 0:
                tweet_lyrics() #tweets random song lyrics every ~2 days
            time.sleep(60)
            count += 1

        # Handle connectivity issues gracefully with a restart of main()
        except (RemoteDisconnected, ConnectionError, ConnectionAbortedError):
            print("Error handled via retry: RemoteDisconnected, Connection Aborted, or Connection Error.")
            main()

if __name__ == "__main__":
    main()