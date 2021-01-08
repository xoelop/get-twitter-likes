import concurrent.futures
import json
import os
import re
import sys
import time
from datetime import datetime
from functools import partial
from typing import List, Tuple

import pandas as pd
import requests
import tweepy
from dotenv import load_dotenv
from fastcore.parallel import parallel
from lxml import etree, html
from requests_html import HTMLSession
from settings import ROOT_DIR
from tqdm import tqdm

sys.path.append('..')

load_dotenv()


def get_url_title_description(url: str, parse_url: bool = True) -> dict:
    default_result = {
        'title': '',
        'description': ''
    }
    if not url or not parse_url:
        return default_result
    try:
        response = requests.get(url, timeout=3)
        content_type = response.headers.get('Content-Type', 'text/html')
        if 'html' in content_type.lower():
            try:
                tree = html.document_fromstring(response.content.decode('UTF-8', 'ignore'))
                result = {
                    'title': get_title(tree),
                    'description': get_description(tree)
                }
            except (etree.ParserError, ValueError) as e:
                return default_result
        else:
            result = default_result

    except requests.exceptions.RequestException as e:
        return default_result
    return result


def get_title(tree) -> str:
    xpaths = [
        '//title/text()[1]',
        "//meta[@name='title']/@content",
        "//meta[@property='og:title']/@content"
    ]
    return get_xpath_results(tree, xpaths)


def get_description(tree) -> str:
    xpaths = [
        "//meta[@name='description']/@content",
        "//meta[@property='og:description']/@content",
    ]
    return get_xpath_results(tree, xpaths)


def parallel_map(function, iterable, max_workers: int = 100, *args, **kwargs, ):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        result = pool.map(partial(function, *args, **kwargs), iterable)
        return list(result)


def get_xpath_results(tree, xpaths) -> str:
    elements = set()
    for xpath in xpaths:
        try:
            xpath_results = tree.xpath(xpath)
            for result in xpath_results:
                elements.add(result)
        except IndexError:
            pass

    elements = list(elements)
    result = ' '.join(elements)
    result = re.sub(r'\s', ' ', result)
    return result


def get_likes_ids(relative_likes_js_path: str):
    input_abs_path = os.path.join(ROOT_DIR, relative_likes_js_path)
    print(f'Reading likes from {input_abs_path}')
    with open(input_abs_path) as input_json:
        data = input_json.read()
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


api = get_tweepy_api()


def parse_date(d: str) -> str:
    return datetime.strptime(d, '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%dT%H:%M:%S.000Z')


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
        'user_follower_count': status.user.followers_count,
        'quoted_status_id': quoted_status_id,
        'json': s,
        'title': title_description.get('title'),
        'description': title_description.get('description'),
    }
    tweet_dict['text'] = ' '.join(set(tweet_dict.get(key, '') for key in ['tweet_text', 'title', 'description']))
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


def split_list_sublists(ids: List, chunksize: int = 100) -> List[List]:
    """Return a list of lists such that the max len of the inner lists is chunksize"""
    ids_chunks = [ids[i*chunksize:i*chunksize+chunksize] for i in range(int(len(ids)/chunksize) + 1)]
    return ids_chunks


def get_all_statuses(input_file: str = 'data/like.js', output_format: str = 'raw', parse_urls: bool = False) -> List[dict]:
    ids = get_likes_ids(input_file)
    ids_lists = split_list_sublists(ids)[:3]
    print('Downloading likes detailed data from Twitter API and parsing their URLs')
    start = time.time()
    tweets_lists = parallel(parse_tweets, ids_lists, output_format=output_format, parse_urls=parse_urls, progress=True, threadpool=True, n_workers=100)
    print(f'Elapsed {time.time() - start:.2f} seconds')
    result = flatten_list(tweets_lists)
    return result


def parse_tweets(statuses_ids: List[str], output_format: str = 'raw', parse_urls: bool = False) -> List[dict]:
    statuses = api.statuses_lookup(statuses_ids, include_entities=True, tweet_mode='extended')
    list_of_lists_of_parsed_tweets = parallel_map(parse_tweet,
                                                  statuses,
                                                  output_format=output_format,
                                                  parse_url=parse_urls)
    parsed_tweets = flatten_list(list_of_lists_of_parsed_tweets)
    return parsed_tweets

def flatten_list(l: List) -> List:
    return [el for sublist in l for el in sublist]  


def create_df_statuses(statuses: List[dict]) -> pd.DataFrame:
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
        'user_follower_count',
        'quoted_status_id',
        'id',
        'json'
    ]
    df = df.reindex(labels=columns, axis=1)
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
