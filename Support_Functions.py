import os
import subprocess
import tweepy
from secrets import declare_secrets

#provide keys and file locations
bearer_token, consumer_key,consumer_secret,access_token,access_token_secret, ranch_photos, joe_lives_photos, cow_photos, food_photos, dog_photos = declare_secrets() #defines secret & API keys & file folders

client = tweepy.Client( 
    bearer_token = bearer_token, consumer_key=consumer_key, 
    consumer_secret=consumer_secret, access_token=access_token, 
    access_token_secret=access_token_secret, wait_on_rate_limit= True
) 

def get_user(client, screen_name):
    print("Start get_user.")
    user = client.get_users(usernames=screen_name) #Uses handle to retrieve user info
    user_id = user.data[0].id #isolates the unique ID for the user as a var
    print("End get_user.")
    return(user, user_id)

def send_tweet(tweet_text):
#prepares a tweet to send.
#Creates and uses a txt file to ensure proper tweet text formatting
    if os.path.exists('tweet_temp.txt'):
        os.remove('tweet_temp.txt')
    with open('tweet_temp.txt', 'w') as text_to_tweet:
        text_to_tweet.write(tweet_text)
    with open('tweet_temp.txt', 'r') as text_to_tweet:
        client.create_tweet(text=text_to_tweet.read())
    return()

def send_tweet_reply_with_photo(status, filename, tweet_id):
    #prepares a tweet to send with media attached.
    #Creates and uses a txt file to ensure proper tweet text formatting
    
    # Create an API object
    auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret, access_token, access_token_secret
    )
    api = tweepy.API(auth, timeout=180)

    if os.path.exists('tweet_temp.txt'):
        os.remove('tweet_temp.txt')
    if os.path.exists('media_file.txt'):
        os.remove('media_file.txt')

    with open('tweet_temp.txt', 'w') as text_to_tweet:
        text_to_tweet.write(status)
    with open('media_file.txt', 'w') as media_file:
        media_file.write(filename)   
    
    with open('media_file.txt', 'r') as media_file:
        media = api.media_upload(filename=media_file.read()) 
    with open('tweet_temp.txt', 'r') as text_to_tweet:
        client.create_tweet(text=text_to_tweet.read(), media_ids=[media.media_id_string], in_reply_to_tweet_id=tweet_id)
    if os.path.exists('tweet_temp.txt'):
        os.remove('tweet_temp.txt')
    if os.path.exists('media_file.txt'):
        os.remove('media_file.txt')
    return()

def quote_tweet(tweet_text, url):
    # Prepares a tweet to send including the url of tweet to quote tweet.
    # This function can be repurposed to tweet with any url link
    # Creates and uses a txt file to ensure proper tweet text formatting
    if os.path.exists('tweet_temp.txt'):
        os.remove('tweet_temp.txt')
    with open('tweet_temp.txt', 'w') as text_to_tweet:
        text_to_tweet.write(tweet_text + " " + url)
    with open('tweet_temp.txt', 'r') as text_to_tweet:
        client.create_tweet(text=text_to_tweet.read())
        print(text_to_tweet.read())
    return()

def commit_and_tweet(commit_message):
    #Caution uses the current environment and adds everything
    #Total message must be less than 280 chars. Commit must be less than 260.
    while len(commit_message) > 260:
        print("Your commit message is too long.")
        commit_message = input("Enter shorter commit message: ")
    subprocess.call(["git", "add", "."])
    subprocess.call(["git", "commit", "-m", commit_message])
    subprocess.call(["git", "push"])
    commit_message = str("Git Commit: " + commit_message)
    client.create_tweet(text=commit_message)
    print("You tweeted: %s" % commit_message)
    print("Tweet Length Was: %s" % (len(commit_message)))
    return()

#send_tweet("")
#send_tweet_with_photo("")
#commit_and_tweet("")

