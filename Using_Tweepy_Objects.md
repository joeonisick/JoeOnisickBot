# Using Tweepy Objects

This Document Describes Using the Tweepy Objects as I understand them. I make no claims to accuracy, this is simply what I've learned that works for using them. If you just want to skip to the part that helps you fix your code, I understand. Here you go: https://github.com/joeonisick/JoeOnisickBot/blob/main/Using_Tweepy_Objects.md#shut-up-and-give-me-the-answer-you-longwinded-moron.

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
When you invoke the class for a valid operation the return is usually a Tweepy model class. This class is where things get interesting. The class stores a lot of data you want, but accessing it isn't always intuitive (alternatively I'm dumb).

Using the following example we invoke the client class with `.get_users_mentions` providing the mandatory user ID (using the user ID for JoeOnisickBot 1554986957532438535). We also provide the optional expansion `author_id` which helps with tying things together. More on this later.
Note: For the purpose of this example I've included a since_id telling the Twitter API to return tweets 'since' meaning newer than that ID. This gets me one response in this example.
```
mentions = client.get_users_mentions(id=user_id,expansions='author_id', since_id=1556257587070488575)
```
That call returns the requested data, storing it in my variable 'mentions'. Quick note: `since_id` and it's companion `until_id` are exclusive. This means that the ID used on either end of your search will not be returned.
When I print mentions we see the following:
```
Response(data=[<Tweet id=1556257587070488576 text='@JoeOnisickBot send cow pic'>], includes={'users': [<User id=15830229 name=danedevalcourt username=danedevalcourt>]}, errors=[], meta={'result_count': 1, 'newest_id': '1556257587070488576', 'oldest_id': '1556257587070488576'})
```
Now the fun part. A quick read of this data is pretty straight forward. We've got:

Some kind of object called `data` which contains:
- `Tweet id: 1556257587070488576` (ID of the returned tweet)
- `Tweet text: '@JoeOnisickBot send cow pic` (The text of the tweet as it would be shown on Twitter)

Another mystery object called `includes` which contains:
- 'users' then contains:
-- User paired with `id: 15830229`, `name: danedevalcourt`, and `username: danedevalcourt`

Another called `errors` which contains an empty list in this case.

Another called `meta` (no not those privacy destroying goat F'rs) which contains:
- `result_count: 1` (The number of responses returned by this invocation of client)
- `newest_id: 1556257587070488576` (The most recent tweet in the response)
- `oldest_id: 1556257587070488576` (The oldest tweet in the response)

These two are the same because only one response was returned.

So far so good. The problem is understanding how to access those mystery objects and their data. The bigger problem is understanding how to correlate between these objects. At a glance it looks like `data` returns a list, but `includes` returns a dictionary. Lists can have duplicate items. Dictionaries cannot have duplicate keys. If we had returned more than one tweet, and two or more came from the same user, we'd have varying object lengths, making it hard to correlate a tweet in `data` with a user in `includes`. In this example: if the operation had returned two tweets from ID `15830229`, `data` would contain them both, while `includes` would remain the same, containing the one unique instance of that ID and its values.

Let's start by digging into the types of mystery objects we have:

First we'll call `print(type(mentions))` on our `mentions` object storing the complete response.
The result `<class 'tweepy.client.Response'>` makes sense. This is the Tweepy model class as described above.

Let's dig further:

- `print(type(mentions.data))` returns `<class 'list'>`
- `print(type(mentions.includes))` returns `<class 'dict'>`
- `print(type(mentions.errors))` returns `<class 'list'>`
- `print(type(mentions.meta))` returns `<class 'dict'>`

We're starting to get somewhere. We've got two lists, and two dictionaries. Dictionaries will let us access a value using its key, while lists will require us to use an index to retrive a specific value. Two things with this return format will complicate your world:

- mentions.data is a list, but each list item contains two things paired as a list item Tweet: `id` and `text`
- The previously mentioned problem with multiple tweets from a given user.

Let's dig down a level:

- `print(mentions.data)` returns `[<Tweet id=1556257587070488576 text='@JoeOnisickBot send cow pic'>]`
A Python list containing a single item with what looks like two values. But how do we access seperate values in a list item?
- `print(mentions.includes)` returns `{'users': [<User id=15830229 name=danedevalcourt username=danedevalcourt>]}`
A Python dictionary containing a key 'users' paired with another multi-value list item.
- `print(mentions.errors)` returns `[]`
Our list of no returned errors.
- `print(mentions.meta)` returns `{'result_count': 2, 'newest_id': '1556257587070488576', 'oldest_id': '1556257587070488576'}`
Our dictionary which includes keys for result_count, newest_id, and oldest id. To me this is the only intuitive object returned. I can use standard dictionary syntax to access any value in `meta` I want.

So, for the love of all that is holy, let's dig down again (skipping `errors` because it's an empty list):

- `print(mentions.data[0])` returns `@JoeOnisickBot send cow pic`

Here's my first extreme WTF moment. When we used `print(mentions.data)` we got `[<Tweet id=1556257587070488576 text='@JoeOnisickBot send cow pic'>]`. That looks like a single list item. When we used `print(mentions.data[0])` to access the first list index, we only get the tweet text. FML. Well, let's go back to checking type...

- `print(type(mentions.data))` returns `<class 'list'>`
Cool, cool. It loos like a list, smells like a list, and amazingly it is a list!
- `print(type(mentions.data[0]))` returns `<class 'tweepy.tweet.Tweet'>`
Tweet tweet: You're killing me now... each list item is a tweepy class `tweepy.tweet.Tweet`. This explains the multiple values stored as a list item. The question becomes "how in the **** do I access the values?" If I just want `text` I'm golden, but let's say I need the ID for a reply tweet?
- `print(mentions.includes['users'])` returns `[<User id=15830229 name=danedevalcourt username=danedevalcourt>]`
This makes some sense. We accessed dictionary key `users` and got the list contained there, which technically has three values in it.
- `print(mentions.meta['result_count'])` returns `1`
Ah, finally, logical and intuitive behavoir. We access a dictionary key and were presented with a piece of usable information stored as a key-value pair.

So now let's dig in yet again. We'll skip `mentions.meta` because it can be utilized like any standard dictionary object. The question we're trying to answer is 'How in Zeus's name do I access the individual value elements within these class objects stored in lists?' We're focused on the the following two class objects:

- The list items in `mentions.data`: `print(type(mentions.data[0]))` which are `<class 'tweepy.tweet.Tweet'>`
-- `print(mentions.data[0])` returns `@JoeOnisickBot send cow pic`

These items are a list of tweepy class objects about the returned tweets. Each includes a tweet `id` and tweet `text` value.
- The list items in `mentions.includes['users']`: `print(type(mentions.includes['users'][0]))` which are `<class 'tweepy.user.User'>`
-- `print(mentions.includes['users'][0])` returns `danedevalcourt`

These items are a list of tweepy class objects about the users. Each includes a user `id`, `name`, and `username` object. Remember, because this is a dictionary, each user will have one unique entry regardless of the number of tweets associated with them.

- Trying `print(mentions.data.id)` returns an error `AttributeError: 'list' object has no attribute 'id'`
- But if we provide the list index (0 for our one item list) `print(mentions.data[0].id)` we hit paydirt with the tweet `id`: `1556257587070488576`
- `print(mentions.data[0].text)` is also successful resulting in `@JoeOnisickBot send cow pic`
So this gets us somewhere. We can iteratre through `mentions.data` and use `text` or `id` to retrieve the value we want. But what else? Let's search tweepy docs using the class we've discovered `tweepy.tweet.Tweet` and we get the info we need https://docs.tweepy.org/en/stable/v2_models.html?highlight=class%20%27tweepy.tweet.Tweet#tweepy.Tweet (kind of). Here we see all of the attributes we can use. The caveat here is they must be returned in the default request or through expansion options you define.
Now lets try the expansion we used in the beginning. You may recall we retrieved mentions using `client.get_users_mentions` and added the optional expansion `expansions='author_id'`. So where in Medusa's fourth kidney is that stinking `author-id`? It seems important, but hasn't shown up in any of our print statements yet. Not in `mentions.data`, `mentions.includes`, or `mentions.meta`. WTF?

Shall we dig? That's rhetorical, I don't care what you think.

- Let's give this a shot: `print(mentions.data[0].author_id)` and amazingly it returns `15830229`. What is this mysterious `author-id`? For that we'll need to explore `mentions.includes` where the user data lives. I'll spoil the surprise for you, it's the user `id` of the tweet author. Interstingly, this doesn't appear anywhere in the commands we've used above, but it should solve our problem of tying `mentions.data` to the user data in `mentions.includes`.

- Trying `print(mentions.includes.id)` returns an error `AttributeError: 'dict' object has no attribute 'id'`. Cool cool, makes sense. `includes` itself is a Python dictionary so it doesn't have attributes, it has key-value pairs. This is unlike `data` which is a list. So let's use the key `users`.
- `print(mentions.includes['users'].id)` returns an error `AttributeError: 'list' object has no attribute 'id'`. Great, further down the rabbit hole we go. Our friend `mentions.includes` is a dictionary with the key `users`, but the key `users` contains a list of users. As stated above, this key contains: `id`, `name`, and `username`. So hopefully indexing the `users` key like we did above for `data` will allow us to use atrributes, only this time we're 5786.98 (estimated) levels deep in a single object.
- `print(mentions.includes['users'][0].id)` returns `15830229` Bingo, bango, blamo! This is the Twitter user `id` in the `tweepy.User` class from the , wait for it:

List at index 0, of the key `users`, of the dictionary `includes` of the Tweepy `tweepy.tweet.Tweet` class. Please shoot me now.

Well, let's make sure the rest of the expected attributes work:
- `print(mentions.includes['users'][0].name)` returns `danedevalcourt` the 'Name' associated with the user's Twitter handle.
- `print(mentions.includes['users'][0].username)` returns `danedevalcourt` the username (Twitter Handle) in this case it happens to be the same.
- `print(mentions.includes['users'][0].author_id)` returns  `AttributeError`. I find this annoying, but I find everything annoying. `author_id` represents the users `id` which is a unique number associated with the twitter handle, and the magic that allows you clowns to constantly change your twitter handles without any negative effect on the rest of the logic.

So... Now that we've reached the, apparent, bottom of the `tweepy.tweet.Tweet` class rabbit hole, how do we tie the values in `mentions.data` to the values in `mentions.includes`? I'm so glad you asked! That last statement is a lie.

Let's start with the basics:
```
for tweet in mentions.data:
    tweet_id = tweet.id
    tweet_text = tweet.text
    author = tweet.author_id
    print("%s was sent by User ID: %s, with Tweet ID: %s" % (tweet_text, author, tweet_id))
```
This returns:
```
@JoeOnisickBot send cow pic was sent by User ID: 15830229, with Tweet ID: 1556257587070488576
```
Here we iterate through `mentions.data`, which contains a list of class `tweepy.tweet.Tweet` values, each containing two visible attributes: `id` and `text`, as well as a mystical `author_id` which is pulled through a space-time wormhole. In our example we only have one tweet, but you now know how to iterate that list and retrive the three criticial associated values: tweet: `id`, `text` and `author_id`.

Next, we may want the rest of the user information associated with that `author_id`, and to have it associated with the tweet. Which kind of feels like a default requirement... For that we can use this:
```
tweet_data = {}
for tweet in mentions.data:
    tweet_data[tweet.id] = {"user_id":tweet.author_id, "tweet_text":tweet.text}

for user in mentions.includes['users']:
    for key in tweet_data:
        if tweet_data[key]["user_id"] == user.id:
            tweet_data[key]["username"] = user.username
            tweet_data[key]["name"] = user.name
print(tweet_data)
```
Which returns these results:
```
{1556257587070488576: {'user_id': 15830229, 'tweet_text': '@JoeOnisickBot send cow pic', 'username': 'danedevalcourt', 'name': 'danedevalcourt'}}
```
This is using the tweet `id` as a unique key paired to a dictionary value. The sub_dictionary populates a `user_id` key using `author_id` ('same' thing), and a `tweet_text` key with the text of the tweet. It then iterates through `mentions.includes['users']` to add the `username`, and `name` to the subdictionary associated with a tweet. This should work for any length return of the `tweepy.client.Response` class. You can now iterate through the dictionary, or grab any specific value you need using `tweet_data[key1][key2]` like such:
```
print(tweet_data[1556257587070488576]['tweet_text'])
```
Which returns the following:
```
@JoeOnisickBot send cow pic
```
If Tweepy originally returned anything like this, I'd have a week of my life back. I've written the code above out in a verbose format for two reasons, it's easier to explain/understand, I have no idea how to write elegant code. There are an infinite number of ways to do this. Most of them more pythonic, more elegant, less processing intensive, whatever. I'm not saying my code doesn't suck, I am saying it works.

### Shut Up and Give me the Answer You Longwinded Moron!
Here is the quick reference for the code solutions above. They all assume you have used Tweepy to return a Tweepy class stored as `mentions` as in the example code.

- `mentions.data`: Tweet data containing tweet `id` and `text` visibly, and `author_id` pulled from the bowels of hell.
-- `mentions.data[x].id`: returns the tweet `id`
-- `mentions.data[x].text`: returns the tweet `text`
-- `mentions.data[x].author_id`: crosses the river styx to obtain the `author_id` from the bowels of Satan's, well, bowels.
- `mentions.includes`: Additional default and optional data about the tweets
-- `mentions.includes['users'][x].id` resturns the user `id`, not to be confused with the tweet `id` above.
-- `mentions.includes['users'][x].name` returns the name of the user (this is not username)
-- `mentions.includes['users'][x].username` returns the username (handle) of the user

If you want to match values from `mentions.data` with values from `mentions.includes` you'll match data's `author_id` with includes' `id`. As an added bonus you must ensure you ask nicely for the `author_id` by placing `expansions='author_id'` in the call to invoke the Tweepy client god. I recommend a standard sacrifice of your choice to accompany the call.

Lastly, if you'd like to use kindergartner code to hack together a dictionary of dictionaries from the results, here you go.
```
tweet_data = {}
for tweet in mentions.data:
    tweet_data[tweet.id] = {"user_id":tweet.author_id, "tweet_text":tweet.text}

for user in mentions.includes['users']:
    for key in tweet_data:
        if tweet_data[key]["user_id"] == user.id:
            tweet_data[key]["username"] = user.username
            tweet_data[key]["name"] = user.name
```

If you read all this. I'm very sorry for your loss. Well that's a lie, the sorry part at least.
