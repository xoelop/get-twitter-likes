from src.core import get_all_statuses, create_df_statuses
import pandas as pd
import argparse

import settings


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-i', '--input', help='Input js file', default='data/like.js')
    parser.add_argument('-o', '--output', help='Destination file', default='data/likes.csv')
    parser.add_argument('-f', '--format', help='Format of specific columns of the csv: raw or gsheets', default='gsheets')
    parser.add_argument('-pu', '--parse-urls', action='store_true', default=False, help='Parse the URL of the tweets that have one')
    args = parser.parse_args()
    input_file = args.input
    output_file = args.output
    output_format = args.format
    parse_urls = args.parse_urls
    # print(args)

    print('Downloading likes detailed data from Twitter API and parsing their URLs')
    likes = get_all_statuses(input_file=input_file,
                             output_format=output_format,
                             parse_urls=parse_urls)
    print(len(likes), 'likes parsed in total')
    df = create_df_statuses(likes)
    df.to_csv(output_file, index=False)
    print(f'Likes saved in {output_file}')
