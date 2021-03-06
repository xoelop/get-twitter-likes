import json
import os
import re
import sys
import time
from datetime import datetime
from typing import List

import pandas as pd
import requests_cache
import tweepy
from fastcore.parallel import parallel
from requests.api import delete
from settings import ROOT_DIR
from tqdm import tqdm

from src.scraping import get_url_title_description
from src.utils import (delete_duplicates_by_key, flatten_list, parallel_map,
                       split_list_sublists)


def get_likes_ids(relative_likes_js_path: str):
    input_abs_path = os.path.join(ROOT_DIR, relative_likes_js_path)
    print(f'Reading likes from {input_abs_path}')
    with open(input_abs_path) as input_json:
        data = input_json.read()
        obj = data[data.find('['): data.rfind(']')+1]
        likes = json.loads(obj)
        ids = [l['like']['tweetId'] for l in likes]
    return ids


def get_tweepy_api(mode='user'):
    """
    mode: str
        'app': Auth as app, read-only. This way the rate limit for
        searches is 450 per 15-min window
        'user': Auth as user, to read and write. Rate limit for
        searches: 180 per 15-min window
    """
    api_key = os.getenv(f'TWITTER_API_KEY')
    api_secret = os.getenv(f'TWITTER_API_SECRET')
    access_token = os.getenv(f'TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv(f'TWITTER_ACCESS_TOKEN_SECRET')

    if mode == 'user':
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
    elif mode == 'app':
        auth = tweepy.AppAuthHandler(api_key, api_secret)

    api = tweepy.API(auth)

    return api


api = get_tweepy_api()


def parse_date(d: str) -> str:
    return datetime.strptime(d, '%a %b %d %H:%M:%S %z %Y')


def parse_tweet(status: tweepy.Status, output_format: str = 'gsheets', parse_url: bool = False) -> List[dict]:
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
        url = s.get('entities', {}).get('urls', [])[-1]['expanded_url']
    except IndexError:
        url = ''
    title_description = get_url_title_description(url, parse_url=parse_url)
    try:
        quoted_status_id = status.quoted_status.id
    except AttributeError:  # no quoted tweet
        quoted_status_id = ''

    tweet_dict = {
        'date': parse_date(s['created_at']),
        'id': status.id_str,
        'link': format_field_link(tweet_link, output_format=output_format),
        'user_logo': format_field_image(logo_user_url, output_format=output_format),
        # 'User alias': f'=HYPERLINK("https://twitter.com/{user_alias}", "@{user_alias}")',
        'screenname': format_field_link(link=f'https://twitter.com/{user_alias}',
                                        text=user_alias,
                                        default_show='text',
                                        output_format=output_format),
        'tweet_text': replace_short_urls_in_text(status.entities, status.full_text),
        'media': format_field_image(media_url_https, output_format=output_format),
        'username': status.user.name,
        'location': status.user.location,
        'bio': replace_short_urls_in_text(status.user.entities, status.user.description),
        'url': url,
        'likes': status.favorite_count,
        'rts': status.retweet_count,
        'num_followers': status.user.followers_count,
        'quoted_status_id': quoted_status_id,
        'json': json.dumps(s),
        'title': title_description.get('title', ''),
        'description': title_description.get('description', ''),
        'insert_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
    }
    if not tweet_dict['title']:
        if s.get('quoted_status', {}):
            tweet_dict['title'] = replace_short_urls_in_text(status.quoted_status.entities,
                                                             status.quoted_status.full_text)
    tweet_dict['text'] = '\n______\n'.join([el for el in [tweet_dict.get(key, '') for key in ['tweet_text', 'title', 'description']] if el])
    if hasattr(status, 'quoted_status'):
        return [tweet_dict, parse_tweet(status.quoted_status, output_format=output_format)[0]]
    else:
        return [tweet_dict]


def format_field_image(value, output_format: str = 'gsheets'):
    value = value.replace('_normal', '_400x400').replace('_200x200', '_400x400')
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


def get_likes_from_json(input_file: str = 'data/like.js', output_format: str = 'raw', parse_urls: bool = False) -> List[dict]:
    ids = get_likes_ids(input_file)
    ids_lists = split_list_sublists(ids)[:]
    print('Downloading likes detailed data from Twitter API and parsing their URLs')
    start = time.time()
    # tweets_lists = []
    # for l in ids_lists:
    #     tweets_lists.append(lookup_and_parse_tweets(l, parse_urls=parse_urls, output_format=output_format))
    tweets_lists = parallel(lookup_and_parse_tweets,
                            ids_lists,
                            output_format=output_format,
                            parse_urls=parse_urls,
                            progress=True,
                            threadpool=True,
                            n_workers=100,
                            pause=0.01)
    print(f'Elapsed {time.time() - start:.2f} seconds')
    result = flatten_list(tweets_lists)
    return result


def lookup_and_parse_tweets(statuses_ids: List[str], output_format: str = 'raw', parse_urls: bool = False) -> List[dict]:
    requests_cache.install_cache(backend='sqlite', expire_after=700000)  # ~8 days
    statuses = api.statuses_lookup(statuses_ids, include_entities=True, tweet_mode='extended')
    requests_cache.uninstall_cache()
    parsed_tweets = parse_tweets(statuses, output_format=output_format, parse_urls=parse_urls)
    return parsed_tweets


def parse_tweets(statuses: List[tweepy.Status],
                 output_format: str = 'raw',
                 parse_urls: bool = False) -> List[dict]:
    list_of_lists_of_parsed_tweets = parallel_map(parse_tweet,
                                                  statuses,
                                                  output_format=output_format,
                                                  parse_url=parse_urls)
    parsed_tweets = flatten_list(list_of_lists_of_parsed_tweets)
    return parsed_tweets


def create_df_statuses(statuses: List[dict], save_json_col: bool = True, output: str = '') -> pd.DataFrame:
    df = pd.DataFrame(statuses)
    columns = [
        'date',
        'link',
        'user_logo',
        'screenname',
        'tweet_text',
        'text',
        'media',
        'username',
        'location',
        'bio',
        'url',
        'title',
        'description',
        'likes',
        'rts',
        'num_followers',
        'quoted_status_id',
        'id',
        'insert_date'
    ]
    if save_json_col:
        columns.append('json')
    df = df.reindex(labels=columns, axis=1)
    if output:
        df.to_csv(output, index=False)
        print(f'{len(df)} likes saved in {output}')
    return df


def replace_short_urls_in_text(entities: dict, text: str) -> str:
    for entity, values in entities.items():
        if isinstance(values, list):
            for el in values:
                text = replace_urls(el, text)
        elif isinstance(values, dict):
            for k, v in values.items():
                for el in v:
                    text = replace_urls(el, text)
    return text


def replace_urls(el: dict, text: str) -> str:
    short_url = el.get('url', '')
    expanded_url = el.get('expanded_url', '')
    if not isinstance(short_url, str) or not isinstance(expanded_url, str):
        return text
    text = text.replace(short_url, expanded_url)
    return text


def get_latest_likes(parse_urls: bool = True, max_id: int = None):
    if max_id:
        likes = api.favorites(screen_name='xoelipedes', count=200, tweet_mode='extended', max_id=max_id, include_entities=True)
    else:
        likes = api.favorites(screen_name='xoelipedes', count=200, tweet_mode='extended', include_entities=True)
    parsed_tweets = parse_tweets(likes, output_format='raw', parse_urls=parse_urls)
    return parsed_tweets


def get_likes(max_calls: int = 5, parse_urls: bool = True) -> List[dict]:
    all_likes = []
    max_id = None
    for i in tqdm(range(max_calls)):
        likes = get_latest_likes(parse_urls=parse_urls, max_id=max_id)
        if not likes:
            break
        sorted_ids = sorted([int(l['id']) for l in likes])
        max_id = sorted_ids[int(len(sorted_ids) * 0.05)]
        all_likes.extend(likes)
    result = delete_duplicates_by_key(all_likes, key='id')
    return result


def save_latest_likes_csv(parse_urls: bool = True, save_json_col: bool = True, output: str = 'data/latest_likes.csv', max_calls: int = 1):
    print(f'Downloading your latest ~{max_calls * 200} likes')
    likes = get_likes(max_calls=max_calls, parse_urls=parse_urls)
    df = create_df_statuses(likes, save_json_col, output=output)
    return df
