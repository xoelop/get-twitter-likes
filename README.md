# Installing
You need `pipenv` installed. If you don't have it, do `pip install pipenv`

Then, do `pipenv install --ignore-pipfile` to install the environment with the required packages

# Getting the data
This is how to get a CSV file containing info for all the tweets you've liked in the past. To do it:
1. Download your Twitter archive. Do it at https://twitter.com/settings/your_twitter_data. It'll take some minutes and you'll get an email when it's done with a link to download your data.

    It'll be a zip containing a bunch of JS files. Copy `like.js` into the folder `data` of the directory where you've cloned the repo.

    I put a `like_example.js` file there; yours should be similar.

2. Create a new Twitter app on https://developer.twitter.com/en/apps, to get the Twitter access tokens you'll need to use the API. More info [here](https://docs.inboundnow.com/guide/create-twitter-application/) on how to do it
    
    The Twitter API is necessary to get detailed info for each tweet. 


3. Create a `.env` file in the root directory, containing your Twitter access tokens:

    ```
    export TWITTER_CONSUMER_KEY=...
    export TWITTER_CONSUMER_SECRET=...
    export TWITTER_ACCESS_TOKEN=...
    export TWITTER_ACCESS_TOKEN_SECRET=...

    export DB_NAME= ...
    export DB_ENDPOINT= ...
    export DB_USER= ...
    export DB_PASSWORD= ...
    export DB_PORT= ...
    ```

4. Run the main script: `pipenv run python get_likes_to_csv.py`

    A new CSV file should have been created in `/data`. It'll be formated in a way that links and images display nicely in Google Sheets

    If you want to create a CSV with just the raw values, run `pipenv run python get_likes_to_csv.py -format raw -o data/likes_raw.csv`

# Bonus
I saved the fav tweets to a spreadsheet on Google Sheets. It's updated every 6h via Integromat

## Saving the past likes in Google Sheets
Just go to https://sheets.new to create a new Google spreadsheet. Then click on `File > Import > Upload` and select the CSV you've just created

## Saving new likes in Google Sheets with Integromat

Integromat is a no-code automation tool that lets you connect hundreds of apps without coding. It's like Zapier on steroids.

If you don't have an Integromat account, create a new one [here](https://www.integromat.com/?pc=xoelipedes). Note - it's an affiliate link, but Integromat has a great free tier that should be enough for this. And if you sign up for the paid account, it'd cost you the same :)

I've created an Integromat scenario that every 6h looks for the tweets I've liked and saves it to the same spreadsheet I've created before. 

You can copy it just creating an empty scenario and importing `twitter_likes_google_sheets_integromat.json`. You'd have to connect your Twitter and Google accounts to Integromat then to make it work.


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
\COPY likes FROM <csv_path>' DELIMITER ',' CSV HEADER;
```

where `<csv_path>` is the full path of your CSV file, like `/Users/xoel/CODE/Projects/twitter_likes/data/likes_raw.csv`

