# Using Tweepy Objects

This Document Describes Using the Tweepy Objects as I understand them. I make no claims to accuracy, this is simply what I've learned that works for using them.

## Tweepy Client Class

For Twitter APIV2 this is the primary Tweepy Class. For those with Twitter Essentials developer access the majority of what you can do lives here.

### Using the Client class

Generally you use this class by calling it with a name of your choice 'client' is used here. You can then use the class by calling that name. 
Use the code below to do that. Replace anything in <> with your developer keys.
I declare these variables using a function in a secrets file that I place in my .gitignore file. Treat secrets like passwords.
```
client = tweepy.Client( 
    bearer_token = <bearer_token>, consumer_<key=consumer_key>, 
    consumer_secret=<consumer_secret>, access_token=<access_token>, 
    access_token_secret=<access_token_secret>
) 
```
When you inovke the class for a valid operation the return is usally a Tweepy model class. This class is where things get interesting. The class stores a lot of data you want, but accessing it isn't always intuitive (alternatively I'm dumb).

Using the following example we invoke the client class with .get_users_mentions providing the mandatory user ID (using the user ID for JoeOnisickBot 1554986957532438535). We also provide the optional expansion 'author_id' which helps with tying things together. More on this later.
Note: For the purpose of this example I've included a since_id telling the Twitter API to return tweets 'since' meaning newer than that ID. This gets me one response in this example.
```
mentions = client.get_users_mentions(id=user_id,expansions='author_id', since_id=1556257587070488575)
```
That call returns the requested data, storing it in my variable 'mentions'. Quick note: since_id and it's companion until_id are exclusive. This means that the ID used on either end of your search will not be returned.
When I print mentions we see the following:
```
Response(data=[<Tweet id=1556257587070488576 text='@JoeOnisickBot send cow pic'>], includes={'users': [<User id=15830229 name=danedevalcourt username=danedevalcourt>]}, errors=[], meta={'result_count': 1, 'newest_id': '1556257587070488576', 'oldest_id': '1556257587070488576'})
```
Now the fun part. A quick read of this data is pretty straight forword. We've got:

Some kind of object called 'data' which contains:
- tweet_id: 1556257587070488576 (ID of the returned tweet)
- text: '@JoeOnisickBot send cow pic' (The text of the tweet as it would be shown on Twitter)

Another mystery object called 'includes' which contains:
- users then includes:
-- User paired with id: 15830229, name: danedevalcourt, and username: danedevalcourt

Another called 'errors' which contains an empty list in this case

Another called 'meta' (no not those privacy destroying goat F'rs) which contains:
- result_count: 1 (The number of responses returned by this invocation of client)
- newest_id: 1556257587070488576 (The most recent tweet in the response)
- oldest_id: 1556257587070488576 (The oldest tweet in the response)
These two are the same because only one response was returned.

So far so good. The problem is understanding how to access them mystery objects and their data. The bigger problem is understanding how to correlate between these objects. At a glance it looks like data returns a list, but includes returns a dictionary. Lists can have duplicate items. Dictionaries cannot have duplicate keys. If we had returned more than one tweet, and two or more came from the same user, we'd have varying object lengths making it hard to correlate a tweet in data, with a user in includes. In this example: if the operation had returned two tweets from ID 15830229, data would contain them both, while includes would remain the same, containing the one unique instance of that ID and its values.

Let's start by digging into the types of mystery objects we have:

First we'll call `print(type(mentions))` on our 'mentions' object storing the complete response.
The result `<class 'tweepy.client.Response'>` makes sense. This is the Tweepy model class as described above.

Let's dig further:
`print(type(mentions.data))` returns `<class 'list'>`
`print(type(mentions.includes))` returns `<class 'dict'>`
`print(type(mentions.errors))` returns `<class 'list'>`
`print(type(mentions.meta))` returns `<class 'dict'>`

We're starting to get somewhere. We've got two lists, and two dictionaries. Dictionaries will let us access a value using its key, while lists will require us to use an index to retrive a specific value. Two things with this return format will complicate your world:

- mentions.data is a list, but each list item contains two things paired as Tweet: id and text
- The previously mentioned problem with multiple tweets from a given user.

Let's dig down a level:

`print(mentions.data)` returns `[<Tweet id=1556257587070488576 text='@JoeOnisickBot send cow pic'>]`
A Python list containing a single item with what looks like two values. But how do we access seperate values in a list item?
`print(mentions.includes)` returns `{'users': [<User id=15830229 name=danedevalcourt username=danedevalcourt>]}`
A Python dictionary containing a key 'users' paired with another multi-value list
`print(mentions.errors)` returns `[]`
Our list of no returned errors
`print(mentions.meta)` returns `{'result_count': 2, 'newest_id': '1556257587070488576', 'oldest_id': '1556257587070488576'}`
Our dictionary which includes keys for result_count, newest_id, and oldest id. To me this is the only intuitive object returned. I can use standard dictionary syntax to access any value in meta I want.

So, for the love of all that is holy, let's dig down again (skipping errors because it's an empty list):

`print(mentions.data[0])` returns `@JoeOnisickBot send cow pic`
Here's my first extreme WTF moment. When we used `print(mentions.data)` we got `[<Tweet id=1556257587070488576 text='@JoeOnisickBot send cow pic'>]`. That looks like a single list item. When we used `print(mentions.data[0])' to access the first list index, we only get the tweet text. FML. Well, let's go back to checking type...
`print(type(mentions.data))` returns `<class 'list'>`
Cool, cool. It loos like a list, smells like a list, and amazingly it is a list!
`print(type(mentions.data[0]))` returns `<class 'tweepy.tweet.Tweet'>`
You're killing me now... each list item is a tweepy class 'tweepy.tweet.Tweet'. This explains the multiple values stored as a list item. The question becomes 'how in the **** do I access the values? If I just want 'text' I'm golden, but let's say I need the ID for a reply tweet?
'print(mentions.includes['users'])' returns `[<User id=15830229 name=danedevalcourt username=danedevalcourt>]`
This makes some sense. We accessed dictionary key 'users' and got the list contained there, which technically has three values in it.
'print(mentions.meta['result_count'])' returns `1`
Ah, finally, logical and intuitive behavoir. We access a dictionary key and were presented with a piece of usable information stored as a key-value pair.

This is as far as I've gotten in expalinging this. I will expand on this over time.

