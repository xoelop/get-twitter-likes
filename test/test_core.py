import pytest
import tweepy
from src.core import get_tweepy_api, get_url_title_description, parse_date, get_likes_ids, parse_status, replace_short_urls_in_text, split_list_sublists
import numpy as np

api = get_tweepy_api()


def test_parse_date():
    assert parse_date('Wed Jan 22 18:14:34 +0000 2020') == '2020-01-22T18:14:34.000Z'


def test_get_likes_ids():
    ids = get_likes_ids()
    print(len(ids))
    assert len(ids)


def test_split_list_sublists():
    ids = np.arange(1, 10000)
    sublists = split_list_sublists(ids)
    print(len(sublists))
    assert sum([len(l) for l in sublists]) == len(ids)


@pytest.mark.parametrize(
    'tweet_id',
    ['1220080725178888193', '1342606758334885895'])
def test_replace_short_urls(tweet_id):
    tweet = api.get_status(tweet_id, tweet_mode='extended')
    full_text = replace_short_urls_in_text(tweet.entities, tweet.full_text)
    assert not 't.co' in full_text
    user_bio = replace_short_urls_in_text(tweet.user.entities, tweet.user.description)
    assert not 't.co' in user_bio


@pytest.mark.parametrize(
    'url',
    [
        'https://www.percona.com/blog/2019/01/14/should-you-use-clickhouse-as-a-main-operational-database/',
        'https://www.julian.com/guide/growth/b2b-sales',
        'https://www.indiehackers.com/post/im-a-salary-negotiation-coach-for-experienced-software-developers-going-to-big-tech-companies-ask-me-anything-d021584177',
        'https://trends.builtwith.com/javascript/jQuery',
    ]
)
def test_get_url_title_description(url):
    title_description = get_url_title_description(url)
    assert title_description.get('title')
    assert title_description.get('description')


def test_parse_tweet_quoted():
    tweet_id_with_quoted_tweet = '1220246340510203904'
    tweet = api.get_status(tweet_id_with_quoted_tweet, tweet_mode='extended')
    parsed_status = parse_status(tweet, parse_url=False)
    assert len(parsed_status) > 1
    assert type(parsed_status[0]) == type(parsed_status[1])
