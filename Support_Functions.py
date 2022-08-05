import os
import subprocess
import tweepy
from secrets import declare_secrets

#API access requirements & Tweepy class creeation
bearer_token, consumer_key,consumer_secret,access_token,access_token_secret \
    = declare_secrets() #function that defines secret & API keys
client = tweepy.Client( 
    bearer_token = bearer_token, consumer_key=consumer_key, 
    consumer_secret=consumer_secret, access_token=access_token, 
    access_token_secret=access_token_secret, wait_on_rate_limit= True
) 


def send_tweet(tweet_text):
#prepares a tweet to send.
#Creates and uses a txt file to ensure proper tweet text formatting
    if os.path.exists('tweet_temp.txt'):
        os.remove('tweet_temp.txt')
    with open('tweet_temp.txt', 'w') as text_to_tweet:
        text_to_tweet.write(tweet_text)
    with open('tweet_temp.txt', 'r') as text_to_tweet:
        #print(text_to_tweet.read())
        client.create_tweet(text=text_to_tweet.read())
    return()

def commit_and_tweet(commit_message):
    #caution uses the current environment and adds everything
    subprocess.call(["git", "add", "."])
    subprocess.call(["git", "commit", "-m", commit_message])


commit_and_tweet("Added function to add, commit, push to git, then tweet the git commit message.")
