import os

import requests_cache

requests_cache.install_cache(backend='sqlite', expire_after=700000)  # ~8 days

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root

if __name__ == "__main__":
    print(ROOT_DIR)
