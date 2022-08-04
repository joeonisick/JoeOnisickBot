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
    bearer_token = bearer_token, consumer_key=consumer_key, 
    consumer_secret=consumer_secret, access_token=access_token, 
    access_token_secret=access_token_secret, wait_on_rate_limit= True
) 

#Screen name to look for
screen_name = "JoeOnisickBot" #The Bots Twitter handle
user = client.get_users(usernames=screen_name) #Uses handle to retrieve user info
user_id = user.data[0].id #isolates the unique ID for the user as a var
#retrieve JoeOnisickBot mentions and their author
mentions = client.get_users_mentions(id=user_id,expansions='author_id',max_results=25)

#create a list of user_ids Joe Bot follows
following = client.get_users_following(user_id,max_results=1000)
followed = []
#print(following)
for i in range(0, following.meta['result_count']):
    followed.append(following.data[i].id)

# #Follow mentions if not already following
list_count = 0 #index var
for user in mentions.includes['users']:
    print(mentions.includes['users'][list_count].username)
    print((mentions.includes['users'][list_count].id) not in followed)
    if (mentions.includes['users'][list_count].id) not in followed:
        client.follow_user(mentions.includes['users'][list_count].id) #follow the user
    list_count += 1

#Tweet something
# print("@%s" % response.includes['users'][i].username)
# client.create_tweet(text=\
#     "Theoretically, I now follow anyone who mentions me. I crave attention. It's loney with only @%s"\
#          % (response.includes['users'][i].username))



#mentions = response.data #Data contians the tweet id and text
#includes = response.includes #includes contains the expansions (author and id)
#print("Includes: %s" % response.includes)
#print(includes['users'])
#print(includes['users'][0].username)
#print(includes['users'][0].id)
#print(mentions)
#print(client.get_users_followers(user_id)) #retrieve followers for an ID
#print(client.get_users_following(user_id)) #retrieve accounts followed for an ID

# #print JoeOnisickBot tweets
# timeline = client.get_users_tweets(user_id)
# for tweet in timeline.data:
#     print(tweet.text)