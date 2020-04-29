import os

import psycopg2
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_ENDPOINT = os.getenv('DB_ENDPOINT', '')
DB_USER = os.getenv('DB_USER', '')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_PORT = os.getenv('DB_PORT', '')

conn = psycopg2.connect(f"""
    host={DB_ENDPOINT} 
    user={DB_USER} 
    password={DB_PASSWORD}
    port={DB_PORT}""")
conn.autocommit = True
cur = conn.cursor()

create_table_likes_statement = """
DROP TABLE IF EXISTS likes;
CREATE TABLE likes (
    date VARCHAR,
    tweet VARCHAR,
    user_logo VARCHAR,
    user_alias VARCHAR,
    text VARCHAR,
    media VARCHAR,
    user_name VARCHAR,
    location VARCHAR,
    user_bio VARCHAR,
    url VARCHAR,
    likes BIGINT,
    rts BIGINT,
    user_follower_count BIGINT,
    logo_user_quoted_tweet VARCHAR,
    quoted_tweet_text VARCHAR,
    user_alias_quoted VARCHAR,
    user_name_quoted VARCHAR,
    id BIGINT
);
"""

print('Dropping table and creating it again')
cur.execute(create_table_likes_statement)
print('Done')