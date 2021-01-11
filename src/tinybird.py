import json
import os

import requests
import settings


def get_tinybird_admin_token():
    tinybird_admin_token = os.getenv('TINYBIRD_ADMIN_TOKEN')
    if not tinybird_admin_token:
        raise ValueError('Go to https://ui.tinybird.com/tokens to get your admin token')
    return tinybird_admin_token


def get_all_likes_ids():
    tinybird_admin_token = get_tinybird_admin_token()
    url = f'https://api.tinybird.co/v0/pipes/twitter_likes_ids.json?token={tinybird_admin_token}'
    response = requests.get(url)
    data = json.loads(response.content)
    ids = data['data'][0]['ids']
    return ids


def append_likes_csv(file: str):
    print('Appending likes CSV to Tinybird ')
    tinybird_admin_token = get_tinybird_admin_token()
    params = {
        'name': 'twitter_likes',
        'mode': 'append',
        'token': tinybird_admin_token,
    }
        
    files = {
        'csv': (file, open(file, 'rb')),
    }

    response = requests.post('https://api.tinybird.co/v0/datasources', params=params, files=files)
    return response