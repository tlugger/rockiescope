import requests
import json
from datetime import datetime
from dateutil import tz
import tweepy
import os
import random
import time
import logging
import logging.handlers

# An official team on July 5th 1991
ROCKIES_SIGN = "cancer"

class Rockiscope():
    def __init__(self):
        self.auth = None
        self.api = None

        # bot epochs
        self.last_baseball_day_sent = datetime(2020, 9, 7, hour=12, tzinfo=tz.gettz('America/Denver'))
        self.last_pi_time_day_sent = datetime(2020, 12, 5, hour=2, tzinfo=tz.gettz('America/Denver'))

    def create_api(self):
        consumer_key = os.getenv("CONSUMER_KEY")
        consumer_secret = os.getenv("CONSUMER_SECRET")
        access_token = os.getenv("ACCESS_TOKEN")
        access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True)
        try:
            self.api.verify_credentials()
            logging.info("Twitter credentials verified")
        except Exception as e:
            logging.error(e)
            raise e
        return self.api

    def send_tweet(self, text):
        status = self.api.update_status(text)
        if status:
            logging.info("Created new tweet")

    # Get todays horiscope for provided sign
    def get_horiscope(self, sign):
        r = requests.post("https://aztro.sameerkumar.website?sign={}&day=today".format(sign))
        return r.json()

    # Get data from nearly unusable MLB stats API
    def get_game_data(self):
        now = datetime.now()
        year = now.year
        date = now.strftime("%Y-%m-%d")
        url = "https://statsapi.mlb.com/api/v1/schedule?lang=en&sportId=1&season={0}&startDate={1}&endDate={1}&teamId=115&&scheduleTypes=games".format(year, date)
        r = requests.get(url)
        return r.json()

    def get_prediction(self, game_time, lucky_time, pct):
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

    def is_pi_time(self, now):
        if now.hour == 15:
            if now.minute == 14:
                if now.second == 15:
                    return True
        return False

# create a default with no games
default_game = {
    "totalGames": 0
}

# make logging
handler = logging.handlers.WatchedFileHandler("./logs/rockiscope.log")
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel("INFO")
root.addHandler(handler)

# switches
do_baseball = False
do_pi_time = True

# make class
r = Rockiscope()

# do bot thing forever
while True:
    now = datetime.now().astimezone(tz.gettz('America/Denver'))
    if now.hour not in [12, 14, 15]:
        time.sleep(1800)
        continue
    if do_pi_time and now.date() > r.last_pi_time_day_sent.date() and r.is_pi_time(now):
        r.send_tweet("Pi Time")
        r.last_pi_time_day_sent = now
    if do_baseball and now.date() > r.last_baseball_day_sent.date() and now.hour == r.last_baseball_day_sent.hour:
        logging.info("Ready to Tweet")
        game_day = r.get_game_data().get('dates', [default_game])[0]
        if game_day['totalGames'] > 0 :
            game = game_day['games'][0]
            
            game_date_str = game['gameDate']
            game_date = datetime.strptime(game_date_str, "%Y-%m-%dT%H:%M:%SZ")
            game_date_mst = game_date.astimezone(tz.gettz('America/Denver'))
            game_time = game_date_mst.strftime("%I:%M %p")

            home_or_away = "home"
            vs_home_or_away = "away"
            if game['teams'][home_or_away]['team']['name'] != "Colorado Rockies":
                home_or_away = "away"
                vs_home_or_away = "home"

            vs = game['teams'][vs_home_or_away]['team']['name']
            pct = game['teams'][home_or_away]['leagueRecord']['pct']

            message = "Game Time: {} vs {}".format(game_time, vs)
            
            horiscope = r.get_horiscope(ROCKIES_SIGN)
            message += "\n\nHoroscope: {}".format(horiscope['description'])

            prediction = r.get_prediction(game_date_mst, horiscope['lucky_time'], pct)
            message += "\n\nPrediction: {}".format(prediction)

            logging.info("Sending: {}".format(message))

            okay = False
            while not okay:
                try:
                    r.create_api()
                    okay = True
                    logging.info("Created Tweepy API")
                    break
                except Exception as e:
                    okay = False
                    time.sleep(30)

            r.send_tweet(message)

        # update last_baseball_day_sent ts after tweet or checking for a game
        r.last_baseball_day_sent = now