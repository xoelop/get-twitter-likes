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
    TWITTER_CONSUMER_KEY=...
    TWITTER_CONSUMER_SECRET=...
    TWITTER_ACCESS_TOKEN=...
    TWITTER_ACCESS_TOKEN_SECRET=...
    ```

4. Run the main script: `pipenv run python get_likes_to_csv.py`

    A new CSV file should have been created in `/data`. 


# Bonus
I saved the fav tweets to a spreadsheet on Google Sheets. It's updated every 6h via Integromat

## Saving the past likes in Google Sheets
Just go to https://sheets.new to create a new Google spreadsheet. Then click on `File > Import > Upload` and select the CSV you've just created

## Saving new likes in Google Sheets with Integromat
I've created an Integromat scenario that every 6h looks for the tweets I've liked and saves it to the same spreadsheet I've created before. 

Create a new scenario and import `twitter_likes_google_sheets_integromat.json`

If you don't have an Integromat account, create a new one [here](https://www.integromat.com/?pc=xoelipedes). Note - it's an affiliate link, Integromat has a great free tier that should be enough for this. And if you'd sign up for the paid account, it'd cost you the same :)

