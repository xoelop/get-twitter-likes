from src.utils import jprint
from src.tinybird import append_likes_csv
from src.core import get_all_statuses, create_df_statuses, save_latest_likes_csv
import pandas as pd
import argparse

import settings


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-o', '--output', help='Destination file', default='data/latest_likes.csv')
    parser.add_argument('-pu', '--parse-urls', action='store_true', default=False, help='Parse the URL of the tweets that have one')
    parser.add_argument('-j', '--save-json-col', action='store_true', default=False, help="Save a JSON column with all the tweet info")
    args = parser.parse_args()
    output_file = args.output
    parse_urls = args.parse_urls
    # print(args)

    df = save_latest_likes_csv(parse_urls=parse_urls,
                               save_json_col=args.save_json_col,
                               output=output_file)
    response = append_likes_csv(file=output_file)
    jprint(response.content)
    # print(len(likes), 'likes parsed in total')
