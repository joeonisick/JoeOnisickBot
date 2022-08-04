import tweepy
from secrets import declare_secrets

#provide keys
bearer_token, consumer_key,consumer_secret,access_token,access_token_secret \
    = declare_secrets() #function that defines secret & API keys

#Twitter rate limt reference: 
#https://developer.twitter.com/en/docs/twitter-api/rate-limits

#Configure the client for use of OAuth1.0 and OAuth2.0 (API object dependant)
#https://developer.twitter.com/en/docs/authentication/guides/v2-authentication-mapping
client = tweepy.Client( 
    bearer_token = bearer_token,
    consumer_key=consumer_key, consumer_secret=consumer_secret,
    access_token=access_token, access_token_secret=access_token_secret
) 

#Screen name to look for
screen_name = "JoeOnisickBot" #The Bots Twitter handle
response = client.get_users(usernames=screen_name) #Uses handle to retrieve user info
user_id = response.data[0].id #isolates the unique ID for the user as a var
print(user_id)

timeline = client.get_users_tweets(user_id)
for tweet in timeline.data:
    print(tweet.text)

#retrieve JoeOnisickBot mentions and their author
response = client.get_users_mentions(id=user_id,expansions='author_id',max_results=25)
#mentions = response.data #Data contians the tweet id and text
#includes = response.includes #includes contains the expansions (author and id)
#print("Includes: %s" % response.includes)
#print(includes['users'])
#print(includes['users'][0].username)
#print(includes['users'][0].id)
#print(mentions)

#print(client.get_users_followers(user_id)) #retrieve followers for an ID
#print(client.get_users_following(user_id)) #retrieve accounts followed for an ID

for i in range(0,len(response.includes)):
    if (response.includes['users'][i].id) not in (client.get_users_following(user_id)):
        client.follow_user(response.includes['users'][i].id) #follow the user

# print("@%s" % response.includes['users'][i].username)
# client.create_tweet(text=\
#     "Theoretically, I now follow anyone who mentions me. I crave attention. It's loney with only @%s"\
#          % (response.includes['users'][i].username))
