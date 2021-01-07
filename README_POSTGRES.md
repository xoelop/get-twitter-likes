
## .env file
Add these lines to your `.env` file
```
    export DB_NAME= ...
    export DB_ENDPOINT= ...
    export DB_USER= ...
    export DB_PASSWORD= ...
    export DB_PORT= ...
```

## Saving tweets to SQL
You can also save your likes data to a SQL database. This code works in Postgres, it'll probably work for other SQL databases with some minimum changes
### Create CSV with raw data
Run `pipenv run python get_likes_to_csv.py -format raw -o data/likes_raw.csv`
### Create SQL table
Run `pipenv run python create_table.py`

### Populate table with the content from the CSV
To do this you need to use psql. Run `source .env` to populate your terminal with you config variables, and then
```
psql \
--host=$DB_ENDPOINT \
--port=$DB_PORT \
--username=$DB_USER \
--password
```
and enter the password of the DB to start a psql session. Then, in SQL, run
```
\COPY likes FROM '<csv_path>' DELIMITER ',' CSV HEADER;
```

where `<csv_path>` is the full path of your CSV file, like `/Users/xoel/CODE/Projects/twitter_likes/data/likes_raw.csv`

In my case, `\COPY likes FROM '/Users/xoel/CODE/Projects/twitter_likes/data/likes_raw.csv' DELIMITER ',' CSV HEADER;
COPY 6472`