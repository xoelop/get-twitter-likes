from src.core import get_all_statuses, create_df_statuses
import pandas as pd
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser('')
    parser.add_argument('--o', '-output', help='Destination file', default='data/likes.csv')
    parser.add_argument('--f', '-format', help='Format of specific columns of the csv: raw or gsheets', default='gsheets')
    args = parser.parse_args()
    output_file = args.o
    output_format = args.f
    print(args)

    print('Downloading likes detailed data from Twitter API')
    likes = get_all_statuses(output_format=output_format)
    df = create_df_statuses(likes)
    df.to_csv(output_file, index=False)
    print(f'Likes saved in {output_file}')
