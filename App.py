import tweepy
import time
from secrets import declare_secrets

#provide keys
bearer_token, consumer_key,consumer_secret,access_token,access_token_secret \
    = declare_secrets() #function that defines secret & API keys

#Twitter rate limt reference: 
#https://developer.twitter.com/en/docs/twitter-api/rate-limits

#Configure the client for use of OAuth1.0 and OAuth2.0 (API object dependant)
#https://developer.twitter.com/en/docs/authentication/guides/v2-authentication-mapping

def get_user(client, screen_name):
    user = client.get_users(usernames=screen_name) #Uses handle to retrieve user info
    user_id = user.data[0].id #isolates the unique ID for the user as a var
    return(user, user_id)

def follow_mention(client, user_id, mentions):
    #create a list of user_ids Joe Bot follows
    following = client.get_users_following(user_id,max_results=1000)
    followed = []
    for i in range(0, following.meta['result_count']):
        followed.append(following.data[i].id)

    #Follow mentions if not already following
    list_count = 0 #index var
    for user in mentions.includes['users']:
        if (mentions.includes['users'][list_count].id) not in followed:
            client.follow_user(mentions.includes['users'][list_count].id) 
        list_count += 1

def check_mentions(client, user_id, since_id):
    #retrieve JoeOnisickBot mentions and their author
    mentions = client.get_users_mentions(id=user_id,expansions='author_id',\
         max_results=100,since_id=since_id)
    #query2 = 'to:JoeOnisickBot -is:reply' #tweets to bot that aren't replies
    query1 = "to:JoeOnisickBot"
    tweets = client.search_recent_tweets(query=query1, expansions =\
         'author_id', max_results=100)
    users = {u["id"]: u for u in tweets.includes['users']}
    for tweet in tweets.data:
        if users[tweet.author_id]:
            user = users[tweet.author_id]
            tweet_id = tweet.id
            query2 = 'from:JoeOnisickBot in_reply_to_tweet_id:'+str(tweet_id)
            results = client.search_recent_tweets(query=query2) 
            if results.meta['result_count'] == 0:
                tweet_text = \
                    (" Thanks for engaging. This reply is the current extent of my communication logic."\
                         % user)
                client.create_tweet(text=tweet_text,in_reply_to_tweet_id=tweet_id)
    new_since_id = mentions.meta['oldest_id']
    follow_mention(client, user_id, mentions)
    return(new_since_id)

def main():
    user_id = 1554986957532438535 #set JoeOnisickBot's user id
    #since ID is set to the first mention of the bot. Since ID is used inclusively.
    since_id = 1555031447047737345 #used to track mentions on the timeline
    client = tweepy.Client( 
        bearer_token = bearer_token, consumer_key=consumer_key, 
        consumer_secret=consumer_secret, access_token=access_token, 
        access_token_secret=access_token_secret, wait_on_rate_limit= True
    ) 
    
    count = 1
    while True:
        since_id = check_mentions(client, user_id, since_id)
        print("While Loop Count: %s" % count)
        time.sleep(120)
        count += 1

if __name__ == "__main__":
    main()
