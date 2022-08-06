#Never gonna give you up 
import tweepy
import random
import os
import time
from secrets import declare_secrets
from Support_Functions import send_tweet, send_tweet_reply_with_photo

#Twitter rate limt reference: 
#https://developer.twitter.com/en/docs/twitter-api/rate-limits

#Configure the client for use of OAuth1.0 and OAuth2.0 (API object dependant)
#https://developer.twitter.com/en/docs/authentication/guides/v2-authentication-mapping

#provide keys and file locations
bearer_token, consumer_key,consumer_secret,access_token,access_token_secret, \
    ranch_photos, joe_lives_photos, cow_photos, food_photos \
        = declare_secrets() #defines secret & API keys & file folders

client = tweepy.Client( 
    bearer_token = bearer_token, consumer_key=consumer_key, 
    consumer_secret=consumer_secret, access_token=access_token, 
    access_token_secret=access_token_secret, wait_on_rate_limit= True
) 

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
            if (mentions.includes['users'][list_count].id) != user_id:
                client.follow_user(mentions.includes['users'][list_count].id)
                tweet_text = ("@%s You mentioned me! Unfortunately, now I must follow you like a stray dog." %  mentions.includes['users'][list_count].username)
                client.create_tweet(text=tweet_text) 
        list_count += 1

def check_mentions(client, user_id, since_id):
    #retrieve JoeOnisickBot mentions and their author
    mentions = client.get_users_mentions(id=user_id,expansions='author_id',\
         max_results=100,since_id=since_id)
    query1 = "to:JoeOnisickBot"
    tweets = client.search_recent_tweets(query=query1, expansions =\
         'author_id', max_results=100,since_id=since_id)
    # I don't know WTF the following code does, or why it works.
    #for dog in dog if dog in dog in other dog do dog...
    if tweets.meta['result_count'] == 0:
        return()
    users = {u["id"]: u for u in tweets.includes['users']}
    for tweet in tweets.data:
        if users[tweet.author_id]:
            user = users[tweet.author_id]
            tweet_id = tweet.id
            # I know what's happening again below this, just haven't debugged
            # I need to stop the reply loop which replies again to reply replies
            query2 = 'from:JoeOnisickBot in_reply_to_tweet_id:'+str(tweet_id)
            results = client.search_recent_tweets(query=query2) 
            if results.meta['result_count'] == 0:
                tweet_text = \
                    (" Thanks for engaging. This reply is the current extent of my communication logic."\
                         % user)
                #client.create_tweet(text=tweet_text,in_reply_to_tweet_id=tweet_id) #needs fixing
    new_since_id = mentions.meta['oldest_id']
    with open('since_id.txt', 'w') as since_id:
        temp = str(since_id)
        since_id.write(temp)
    follow_mention(client, user_id, mentions)
    return(new_since_id)

def retrieve_image(image_type):
    # supported image_types are: 
    # ranch, joe_lives_photos, cow_photos, food_photos
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
    timestamp = ("%s/%s/%s - %s:%s %s" % (month, day, year, hour, minute, period))

    try:
        photo = open(file)
        photo.close()
    except IOError:
        print("File not found.")
    return(file, timestamp, picture)

def check_photo_requests(photo_since):
    #uses a .txt file to simplify passing arguments cleanly
    with open('photo_query.txt', 'r') as photo_query:
        tweets = client.search_recent_tweets(query=photo_query.read(),expansions='author_id',max_results=100,since_id=photo_since)
    if tweets.meta['result_count'] == 0:
        return()
    for tweet in tweets.data:
        print(tweet.text)
        print(tweet.id)
    users = {u["id"]: u for u in tweets.includes['users']}
    for tweet in tweets.data:
        if users[tweet.author_id]:
            user = users[tweet.author_id]
            tweet_id = tweet.id
            if "joe alive?" in tweet.text.lower(): 
                image_type = joe_lives_photos
                name = "Joe"
            elif "send me cows" in tweet.text.lower(): 
                image_type = cow_photos
                name = "cow"
            elif "send me food" in tweet.text.lower(): 
                image_type = food_photos
                name = "food"
            elif "send me ranch" in tweet.text.lower(): 
                image_type = ranch_photos
                name = "ranch"
            else:
                return()
        file, timestamp, picture = retrieve_image(image_type)
        print("Retrieved %s, from %s, with timestamp %s" % (picture, file, timestamp))
        if name == "Joe":
            print("@%s As of %s Joe was alive. Here's your requested proof of life." % (user, timestamp))
            send_tweet_reply_with_photo("@%s As of %s Joe was alive. Here's your requested proof of life." % (user, timestamp), file, tweet_id)
        else:
            print("@%s Here's the %s photo you requested. It was taken at %s." % (user, name, timestamp))
            send_tweet_reply_with_photo(("@%s Here's the %s photo you requested. It was taken at %s." % (user,name, timestamp)), file, tweet_id)
    
    photo_since = tweets.meta['oldest_id']
    with open('photo_since.txt', 'w') as photo_since:
        temp = str(photo_since)
        photo_since.write(temp)
    return(photo_since)

def main():
    user_id = 1554986957532438535 #set JoeOnisickBot's user id
    # since_id is set to the oldest tweet replied to. Since ID is used inclusively.
    with open('since_id.txt', 'r') as since_id:
        since_id = int(since_id.read())
    # photo_since is set to the oldest photo sent. Since ID is used inclusively.
    with open('photo_since.txt', 'r') as photo_since:
        photo_since = int(photo_since.read())

    count = 1
    while True:    
        since_id = check_mentions(client, user_id, since_id)
        photo_since = check_photo_requests(photo_since)
        print("While Loop Count: %s" % count)
        time.sleep(120)
        count += 1


if __name__ == "__main__":
    main()
