# %%

import json
import os
import sys
from datetime import datetime
from functools import lru_cache
from typing import List, Tuple

import pandas as pd
import tweepy
from dotenv import load_dotenv
from pandas.io.json import json_normalize
from tqdm import tqdm

from config import ROOT_DIR

sys.path.append('..')

load_dotenv()


def get_likes_ids():
    with open(f'{ROOT_DIR}/data/like.js') as dataFile:
        data = dataFile.read()
        obj = data[data.find('['): data.rfind(']')+1]
        likes = json.loads(obj)
        ids = [l['like']['tweetId'] for l in likes]

    return ids


def get_tweepy_api():
    consumer_key = os.getenv(f'TWITTER_CONSUMER_KEY')
    consumer_secret = os.getenv(f'TWITTER_CONSUMER_SECRET')
    access_token = os.getenv(f'TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv(f'TWITTER_ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    return api


def parse_date(d: str) -> str:
    return datetime.strptime(d, '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%dT%H:%M:%S.000Z')


def parse_status(status: tweepy.Status) -> dict:
    s = status._json
    tweet_link = f'https://twitter.com/{s["user"]["screen_name"]}/status/{s["id_str"]}'
    logo_user_url = s['user']['profile_image_url_https'].replace(
        'normal.jpg', '200x200.jpg')
    user_alias = status.user.screen_name
    try:
        media_url_https = s.get('entities', {}).get(
            'media', [])[0]['media_url_https']
    except IndexError:
        media_url_https = ''
    try:
        url = s.get('entities', {}).get('urls', [])[0]['expanded_url']
    except IndexError:
        url = ''
    try:
        quoted_status_user_logo = f'=IMAGE("{status.quoted_status.user.profile_image_url_https.replace("normal.jpg", "200x200.jpg")}", 1)'
        quoted_status_tweet = f' {status.quoted_status.full_text}'
        quoted_user_alias = status.quoted_status.user.screen_name
        quoted_user_name = status.quoted_status.user.name
    except AttributeError:  # no quoted tweet
        quoted_status_user_logo = quoted_status_tweet = quoted_user_alias = quoted_user_name = ''

    result = {
        'Date': parse_date(s['created_at']),
        'ID': status.id_str,
        'Tweet': f'=HYPERLINK("{tweet_link}")',
        'User logo': f'=IMAGE("{logo_user_url}", 1)',
        'User alias': f'=HYPERLINK("https://twitter.com/{user_alias}", "@{user_alias}")',
        'Text': f' {s["full_text"]}',
        'Media': f'=IMAGE("{media_url_https}", 1)',
        'User name': status.user.name,
        'Location': status.user.location,
        'User bio': status.user.description,
        'URL': url,
        'Likes': status.favorite_count,
        'RTs': status.retweet_count,
        'User follower count': status.user.followers_count,
        'Logo user quoted tweet': quoted_status_user_logo,
        'Quoted tweet text': quoted_status_tweet,
        'User alias quoted': quoted_user_alias,
        'User name quoted': quoted_user_name,
    }
    return result


def split_list_sublists(ids: List) -> List[List]:
    """Return a list of lists such that the max len of the inner lists is 100"""
    ids_chunks = [ids[i*100:i*100+100] for i in range(int(len(ids)/100) + 1)]
    return ids_chunks


@lru_cache(maxsize=200)
def get_statuses(ids: Tuple) -> List[tweepy.Status]:
    api = get_tweepy_api()
    statuses = api.statuses_lookup(ids, include_entities=True, tweet_mode='extended')
    return statuses


def get_all_statuses() -> List[dict]:
    ids = get_likes_ids()
    ids_lists = split_list_sublists(ids)
    result = []
    for ids_sublist in tqdm(ids_lists):
        statuses = get_statuses(tuple(ids_sublist))
        parsed_tweets = [parse_status(s) for s in statuses]
        result = result + parsed_tweets
    return result


def create_df_statuses(statuses: List[dict]) -> pd.DataFrame:
    df = pd.DataFrame(statuses)
    columns = ['Date',
            'Tweet',
            'User logo',
            'User alias',
            'Text',
            'Media',
            'User name',
            'Location',
            'User bio',
            'URL',
            'Likes',
            'RTs',
            'User follower count',
            'Logo user quoted tweet',
            'Quoted tweet text',
            'User alias quoted',
            'User name quoted', 
            'ID',
            ]
    df = df.reindex(labels=columns, axis=1)
    return df