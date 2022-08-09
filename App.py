#Never gonna give you up 
from http.client import RemoteDisconnected
import tweepy # Twitter API access module
import random # Random Choices
import os # File access
import time # wait, etc.
import pickle # Read/Write binary files to persistently store vars
from secrets import declare_secrets
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
    following = client.get_users_following(user_id,max_results=50)
    followed = []

    # Create a user ID list of users JoeOnisickBot already follows
    for i in range(0, following.meta['result_count']):
        followed.append(following.data[i].id)

    # Store reponses from follow_responses.txt as a list
    with open('follow_responses.txt', 'r') as responses:
        follow_responses = responses.read().split("\n")

    # Follow mentions if not already following
    list_count = 0 #index var
    #iterate through the returned data and parse mentions
    for user in mentions.includes['users']:
        # Verify the user isn't already being followed
        if (mentions.includes['users'][list_count].id) not in followed:
            # Verify the user isn't JoeOnisickBot
            # This prevents 'follow self' errors
            if (mentions.includes['users'][list_count].id) != user_id:
                # Follow the user
                client.follow_user(mentions.includes['users'][list_count].id)
                
                tweet_id = mentions.data[list_count].id # Gets the tweet ID to reply to.
                response = random.choice(follow_responses) #choose random response
                tweet_text = ("@%s %s" % (str(mentions.includes['users']\
                    [list_count].username), str(response)))

                # Create a tweet using the three variable defined above    
                #client.create_tweet(text=tweet_text, in_reply_to_tweet_id=tweet_id)  Need logic that doesn't suck
                print(tweet_text)

        list_count += 1 # Update the index number

    print("End follow_mentions.")
    return()

def check_mentions(client, user_id):
    print("Start check_mentions.")
    # Retrieve JoeOnisickBot mentions and their author
    # Twitter defines mentions as @user as the first part of the string
    # Using the search function it's possible to pull all @'s within limits

    # Since_id is set to the newest tweet replied to.
    since_id = read_since("mentions")

    # with open('since_id.txt', 'r') as tmp_text:                  # Test then remove
    #     since_id = int(tmp_text.read())                          # Test then remove

    # Retrieves mentions since (since_id) the last run
    mentions = client.get_users_mentions(id=user_id,expansions='author_id',\
         max_results=100,since_id=since_id)
    
    # Return if the query has no results
    if mentions.meta['result_count'] == 0:
        return()

    # with open('since_id.txt', 'w') as temp_txt:                  # Test then remove
    #     temp_txt.write(str(since_id))                            # Test then remove
   
    # Follows the person mentioning the bot
    # Sends them a notifcation reply
    follow_mention(client, user_id, mentions)

    # Stores the newest tweet ID and rewrites since_id file
    since_id = mentions.meta['newest_id']
    write_since(since_id, "mentions")

    print("End check_mentions.")
    return()

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
    
    # since_id is set to the newest photo request sent tweet_id. 
    since_id = read_since("photo")
    
    # Pull the query from text to ensure proper string parsing
    with open('photo_query.txt', 'r') as photo_query:
        tweets = client.search_recent_tweets(query=photo_query.read()\
            ,expansions='author_id',max_results=100,since_id=since_id)
    
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
    since_id = tweets.meta['newest_id']

    # Save the new since_id to file
    write_since(since_id, "photo")

    # with open('photo_since.txt', 'w') as tmp_text:                       # Test then remove
    #     tmp_text.write(str(photo_since))                                 # Test then remove

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

    # since_id is set to the tweet ID of newest #JoeOnisick mention replied to.
    since_id = read_since("stalk")

    # with open('stalk_since.txt', 'r') as tmp_text:                     # Test then delete
    #     stalk_since = int(tmp_text.read())                             # Test then delete

    # Search for #JoeOnisick mentions since the last parsed
    tweets = client.search_recent_tweets(query="#JoeOnisick",\
    expansions='author_id',max_results=100,since_id=since_id)
    
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

    since_id = tweets.meta['newest_id']
    write_since(since_id, "stalk")
    
    # with open('stalk_since.txt', 'w') as tmp_text:                         # Test the delete
    #     tmp_text.write(str(stalk_since))                                   # Test then delete
    
    print("End stalk_joeonisick")
    return()

def feature_request():
    # Allows users to request features. Building them is not implied.
    print("Start feature_request.")
    
    # Get the ID of the last request responded to.
    since_id = read_since("feature")

    # with open('feature_since.txt', 'r') as feature_since:                     # Test then delete
    #     feature_since = int(feature_since.read())                             # Test then delete
    
    # Search for 'feature' and 'request' Twitter's API treats a space as and.
    tweets = client.search_recent_tweets(query="@JoeOnisickBot feature request"\
        ,expansions='author_id',max_results=100,since_id=since_id)
    
    # Return if the query has no results
    if tweets.meta['result_count'] == 0:
        return()
    
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

            send_tweet_reply(status, tweet_id)
            print(status)

    # Update the since ID to persistent storage
    since_id = tweets.meta['newest_id']
    write_since(since_id, "feature")

    # with open('feature_since.txt', 'w') as feature_since:v              # Test then delete
    #     feature_since.write(str(tweet_id))                              # Test then delete
    
    print("End feature_request.")
    return()

def write_since(since_id, type):
    # Used to persistently store since_ids to a file.
    # Pickles the since_ids dictionary.
    # since_id is the ID to store
    # Type dictates the dictionary key/since_id use
    print("Start write_since.")

    # Read the existing dictionary in order to modify it
    with open('perm_objects/since_ids.pickle', 'rb') as f:
        since_ids = pickle.load(f)
        # Modify the corresponding since_ids dict key
        since_ids[type] = int(since_id)
        #print(since_ids)

    # Write the dictionary to file
    with open('perm_objects/since_ids.pickle', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(since_ids, f, pickle.HIGHEST_PROTOCOL)

    print("End write_since.")
    return()

def read_since(type):
    # Used to retrieve persistently stored since_ids.
    # Unpickles the since_ids dictionary.
    # Type dictates the dictionary key/since_id use
    print("Start read_since.")
    
    # Unpickle and read the file
    with open('perm_objects/since_ids.pickle', 'rb') as f:
        since_ids = pickle.load(f)
        since_id = since_ids[type]
        #print(since_id)
    print("End read_since.")
    return(since_id)

def user_help():
    # Searches for JoeOnisickBot mentions including 'help' and replies
    print("Start user_help.")

    # Sets the since_id to the tweet ID of the last request
    since_id = read_since('help')

    # Pull the query from text to ensure proper string parsing
    # Search for #JoeOnisick mentions since the last parsed
    tweets = client.search_recent_tweets(query="@JoeOnisickBot help options"\
        ,expansions='author_id',max_results=100,since_id=since_id)

    if tweets.meta['result_count'] == 0:
        return()

    with open('Interactions.txt', 'r') as tmp_text:
        tweet_text = tmp_text.read()
    # Iterate through return and parse replies
    users = {u["id"]: u for u in tweets.includes['users']}
   
    for tweet in tweets.data:
        if users[tweet.author_id]:
            user = users[tweet.author_id]
            tweet_id = tweet.id
            status = ("@%s %s" % (user,tweet_text))
            client.create_tweet(text=tweet_text, in_reply_to_tweet_id=tweet_id)
    
    # Update the since ID to persistent storage
    since_id = tweets.meta['newest_id']
    write_since(since_id, "help")

    print("End user_help.")
    return()

def main():
    print("Start main.")
    user_id = 1554986957532438535 #set JoeOnisickBot's user id

    count = 1
    while True:
        try:  
            user_help()
            stalk_joeonisick()
            time.sleep(20)
            check_mentions(client, user_id)
            time.sleep(20)
            check_photo_requests()
            time.sleep(20)
            feature_request()
            print("While Loop Count: %s" % count) # Tracking
            if count % 3000 == 0:
                tweet_lyrics() #tweets random song lyrics every ~2 days
            count += 1
        
        # Handle connectivity issues gracefully with a restart of main()
        except (RemoteDisconnected, ConnectionError, ConnectionAbortedError):
            print("Error handled via retry: RemoteDisconnected, Connection Aborted, or Connection Error.")
            main()

if __name__ == "__main__":
    main()



