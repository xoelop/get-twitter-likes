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
    ```

4. Run the main script: `pipenv run python get_likes_to_csv.py`
   
   Here are the available options:
    ```   
    usage: get_likes_to_csv.py [-h] [-i INPUT] [-o OUTPUT] [-f FORMAT] [-pu]

    optional arguments:
    -h, --help            show this help message and exit
    -i INPUT, --input INPUT
                            Input js file (default: data/like.js)
    -o OUTPUT, --output OUTPUT
                            Destination file (default: data/likes.csv)
    -f FORMAT, --format FORMAT
                            Format of specific columns of the csv: raw or gsheets (default: gsheets)
    ```

    A new CSV file should have been created in `/data`. It'll be formated in a way that links and images display nicely in Google Sheets

    If you want to create a CSV with just the raw values, run `pipenv run python get_likes_to_csv.py -i data/like_example.js -f raw -o data/likes_example.csv`



## Saving the past likes on Tinybird

Go to https://ui.tinybird.com/login to create a Tinybird account

Create a data source with your likes csv file called `twitter_likes`

Create a pipe called `query_likes` containing these nodes

// TODO

Add your Tinybird admin token from https://ui.tinyibird.com/tokens to your .env file

## Keeping your likes file updated on Tinybird

Run `pipenv run python upload_latest_likes.py`

// TODO