import json
import os

import requests
import settings

from src.utils import jprint


def get_tinybird_admin_token():
    tinybird_admin_token = os.getenv('TINYBIRD_ADMIN_TOKEN')
    if not tinybird_admin_token:
        raise ValueError('Go to https://ui.tinybird.com/tokens to get your admin token')
    return tinybird_admin_token


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
    data = json.loads(response.content)
    print(f"Data imported to the {data['datasource']['name']} datasource. Check it out at https://ui.tinybird.co/datasource/{data['datasource']['id']}")
    if errors := data.get("error", ""):
        print(f'errors: {errors}')
    else:
        print('No errors')
    return data
