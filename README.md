# JoeOnisickBot
This non-innovative and non-intuitive project replaces the real life Joe Onisick with something far more useful. Namely a Twitter bot with minimal functionality. The application interfaces with users through its Twitter account @JoeOnisickBot. The bot is designed to engage with users and provide a Joe Onisick experience that, unlike the real version, is based on logic. In this case logic in the form of Python code written by someone with no idea what they're doing.

## Prerequisites

- Python3.5 and above
- In your Python virtual environment terminal type `python -v` to check your version.

## Getting Started

These instructions will get you moving with your own low-function (unlike low-code) Twitter Bot.
- Sign up for a Twitter devleoper acocunt. Your inital Essential access will work for this project. https://developer.twitter.com/
- Clone this repository using `git clone https://github.com/joeonisick/JoeOnisickBot.git`
- Install Tweepy `pip install tweepy`
- Tweepy Install Documentation: https://docs.tweepy.org/en/stable/install.html
- Tweepy Getting Started Documentation: https://docs.tweepy.org/en/stable/getting_started.html
- Tweepy Note: Tweepy's documentaiton is a dumpster fire, and their object use isn't very intuitive.
- Tweepy Note: When searching for Tweepy help pay close attention Twitter is between API versions so many answers don't work.
- Switch to the project directory: `cd JoeOnisickBot`
- I have not yet created a requirements doc, so you're on your own from here.

To use the project you will need the following files:
- App.py: Contains the main program functions. This is the file you will run to start the bot.
- Support_Functions.py: This file contains functions used by the program, as well as some functions for maintenance and support.
  - General functions like send_tweet live here and are called by App.py. Other functions like commit_and_tweet can be used here as desired.
- perm_objects\new_since_id.pickle: binary file used to store Twitter since_id persistently
- Response_Options\follow_reponses.txt: used to store a list of responses that can be randomly used to generate tweets after following someone
- perm_objects\song_lyrics: used to store out of context lyrics used by a function to tweet a random one every ~3 hours.
- secrets.py: ENSURE THIS IS IN YOUR .gitignore. This declares API keys and file locations returning them from a function.
- Example_Secrets: Example Secrets files with placeholders for your keys and directories. Rename and add to .gitignore before adding keys.
- Using_Tweepy_Objects.md: When you start pulling your hair out using Tweepy, start here (seriously, before you go anywhere else.)

## Built With

- Tweepy
- Twitter API V1 & V2 (object dependant). Currently this project will fully function with a Twitter Developer Essential account.

## Contributing

Contributions to this project are welcome. Be warned in advance that the project owner is clueless as to how to manage a project. If you'd like to contribute you may have to coach him through the process. By coach I mean, treat him like a very dumb child.

## Versioning

Currently there is only one version. As soon as the author figures out versioning best practices this will be updated.

## License

Pending some research.

## Future Plans

This app will be containerized and designed to run cloud native using cloud storage buckets.


