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
    ranch_photos, joe_lives_photos, cow_photos, food_photos, dog_photos \
        = declare_secrets() #defines secret & API keys & file folders

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

def follow_mention(client, user_id, mentions):
    print("Start follow_mentions.")
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
                print("@%s You mentioned me! Unfortunately, now I must follow you like a stray dog." %  mentions.includes['users'][list_count].username)
                tweet_text = ("@%s You mentioned me! Unfortunately, now I must follow you like a stray dog." %  mentions.includes['users'][list_count].username)
                client.create_tweet(text=tweet_text) 
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
    timestamp = ("%s/%s/%s - %s:%s %s" % (month, day, year, hour, minute, period))

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
        tweets = client.search_recent_tweets(query=photo_query.read(),expansions='author_id',max_results=100,since_id=photo_since)
    if tweets.meta['result_count'] == 0:
        return()

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
            elif "send me dog" in tweet.text.lower():
                image_type = dog_photos
                name = "dog"
            else:
                return()
        file, timestamp, picture = retrieve_image(image_type)
        if name == "Joe":
            print("@%s As of %s Joe was alive. Here's your requested proof of life." % (user, timestamp))
            send_tweet_reply_with_photo("@%s As of %s Joe was alive. Here's your requested proof of life." % (user, timestamp), file, tweet_id)
        else:
            print("@%s Here's the %s photo you requested. It was taken at %s." % (user, name, timestamp))
            send_tweet_reply_with_photo(("@%s Here's the %s photo you requested. It was taken at %s." % (user,name, timestamp)), file, tweet_id)
    
    photo_since = tweets.meta['newest_id']
    with open('photo_since.txt', 'w') as tmp_text:
        tmp_text.write(str(photo_since))
    print("End check_photo_requests.")
    return()

def main():
    print("Start main.")
    user_id = 1554986957532438535 #set JoeOnisickBot's user id

    count = 1
    while True:    
        check_mentions(client, user_id)
        check_photo_requests()
        print("While Loop Count: %s" % count)
        time.sleep(120)
        count += 1

if __name__ == "__main__":
    main()
