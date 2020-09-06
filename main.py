import requests
import json
from datetime import datetime
from dateutil import tz
import tweepy
import os
import random
import time

# An official team on July 5th 1991
ROCKIES_SIGN = "cancer"

def create_api():
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, 
        wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        raise e
    return api

def send_tweet(text):
    api = create_api()
    status = api.update_status(text)

# Get todays horiscope for provided sign
def get_horiscope(sign):
    r = requests.post("https://aztro.sameerkumar.website?sign={}&day=today".format(sign))
    return r.json()

# Get data from nearly unusable MLB stats API
def get_game_data():
    now = datetime.now()
    year = now.year
    date = now.strftime("%Y-%m-%d")
    url = "https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&season={0}&startDate={1}&endDate={1}&teamId=115&&scheduleTypes=games".format(year, date)
    r = requests.get(url)
    return r.json()

def get_prediction(game_time, lucky_time, pct):
    win = False
    game_hour = game_time.hour
    lucky_hour = int(lucky_time[0:-2])
    if lucky_time.endswith("pm"):
        lucky_hour += 12
    
    time_delta = abs(lucky_hour-game_hour)
    if time_delta == 0:
        return "W"

    # don't ask
    stonks = (float(pct) + (1/(time_delta)))/2
    if random.random() < stonks:
        win = True
    
    return "W" if win else "L"

# create a default with no games
default_game = {
    "totalGames": 0
}

# bot epoch
last_day_sent = datetime(2020, 9, 5, hour=12, tzinfo=tz.gettz('America/Denver'))

# do bot thing forever
while True:
    time.sleep(5)
    now = datetime.now()
    if now.date() > last_day_sent.date():
        if now.hour == last_day_sent.hour:
            game_day = get_game_data().get('dates', [default_game])[0]
            if game_day['totalGames'] > 0 :
                game = game_day['games'][0]
                
                game_date_str = game['gameDate']
                game_date = datetime.strptime(game_date_str, "%Y-%m-%dT%H:%M:%SZ")
                game_date_mst = game_date.astimezone(tz.gettz('America/Denver'))
                game_time = game_date_mst.strftime("%I:%M %p")

                home = game['teams']['home']['team']['name']
                away = game['teams']['away']['team']['name']
                
                pct = game['teams']['away']['leagueRecord']['pct']
                if home == "Colorado Rockies":
                    pct = game['teams']['home']['leagueRecord']['pct']

                message = "Game Time: {}\n\nHome: {}\nAway: {}".format(game_time, home, away)
                
                horiscope = get_horiscope(ROCKIES_SIGN)
                message += "\n\nHorisope: {}".format(horiscope['description'])

                prediction = get_prediction(game_date_mst, horiscope['lucky_time'], pct)
                message += "\n\nOutcome Prediction: {}".format(prediction)

                send_tweet(message)

            # update last_day_sent ts after tweet or checking for a game    
            last_day_sent = now    

