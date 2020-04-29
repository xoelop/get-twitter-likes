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


def parse_status(status: tweepy.Status, output_format: str = 'gsheets') -> dict:
    """
    Creates a dictionary with the fields I'm interested in to save from each tweet

    output_format: str, default 'gsheets':
        'ghseets': Adds special syntax for certain elements, like =IMAGE(...) or =HYPERLINK(...)
            so that those columns render nicely in Google Sheets
        'raw': Saves just the raw data for each column
    """
    s = status._json
    tweet_link = f'https://twitter.com/{s["user"]["screen_name"]}/status/{s["id_str"]}'
    logo_user_url = s['user']['profile_image_url_https'].replace('normal.jpg', '200x200.jpg')
    user_alias = status.user.screen_name
    try:
        media_url_https = s.get('entities', {}).get('media', [])[0]['media_url_https']
    except IndexError:
        media_url_https = ''
    try:
        url = s.get('entities', {}).get('urls', [])[0]['expanded_url']
    except IndexError:
        url = ''
    try:
        quoted_status_user_logo = format_field_image(
            status.quoted_status.user.profile_image_url_https.replace("normal.jpg", "200x200.jpg"),
            output_format=output_format)
        quoted_status_tweet = format_field_text(status.quoted_status.full_text,
                                                output_format=output_format)
        quoted_user_alias = status.quoted_status.user.screen_name
        quoted_user_name = status.quoted_status.user.name
    except AttributeError:  # no quoted tweet
        quoted_status_user_logo = quoted_status_tweet = quoted_user_alias = quoted_user_name = ''

    result = {
        'Date': parse_date(s['created_at']),
        'ID': status.id_str,
        'Tweet': format_field_link(tweet_link, output_format=output_format),
        'User logo': format_field_image(logo_user_url, output_format=output_format),
        # 'User alias': f'=HYPERLINK("https://twitter.com/{user_alias}", "@{user_alias}")',
        'User alias': format_field_link(link=f'https://twitter.com/{user_alias}',
                                        text=user_alias,
                                        default_show='text',
                                        output_format=output_format),
        'Text': format_field_text(s["full_text"], output_format=output_format),
        'Media': format_field_image(media_url_https, output_format=output_format),
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


def format_field_image(value, output_format: str = 'gsheets'):
    if output_format == 'gsheets':
        result = f'=IMAGE("{value}", 1)'
    elif output_format == 'raw':
        result = value
    return result


def format_field_link(link: str = '', text: str = '', default_show: str = 'text', output_format: str = 'gsheets'):
    if output_format == 'gsheets':
        if text:
            result = f'=HYPERLINK("{link}", "{text}")'
        else:
            result = f'=HYPERLINK("{link}")'
    elif output_format == 'raw':
        if default_show == 'text':
            result = text if text else link
        else:
            result = link if link else text
    return result


def format_field_text(text: str, output_format: str = 'gsheets'):
    if output_format == 'gsheets':
        result = f' {text}'
    elif output_format == 'raw':
        result = text
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


def get_all_statuses(output_format: str = 'raw') -> List[dict]:
    ids = get_likes_ids()
    ids_lists = split_list_sublists(ids)
    result = []
    for ids_sublist in tqdm(ids_lists):
        statuses = get_statuses(tuple(ids_sublist))
        parsed_tweets = [parse_status(s, output_format=output_format) for s in statuses]
        result = result + parsed_tweets
    assert len(result) > 0
    return result


def create_df_statuses(statuses: List[dict]) -> pd.DataFrame:
    df = pd.DataFrame(statuses)
    columns = [
        'Date',
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
