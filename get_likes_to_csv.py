from src.core import get_all_statuses, create_df_statuses
import pandas as pd

print('Downloading likes detailed data from Twitter API')
likes = get_all_statuses()
df = create_df_statuses(likes)
df.to_csv('likes.csv')
print('Likes saved in data/likes.csv')
