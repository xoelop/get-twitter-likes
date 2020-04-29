# Scope of the project

I created this project to solve a problem of mine: sometimes I'd want to find a tweet that I had liked some time ago and there was no easy way to do it. With this project, I attempted to create an archive of my likes so that I can make searches and queries on them.

## The problem

Going to the 'Likes' tab in your Twitter profile and doing a CMD-F search doesn't work because it updates the DOM as you scroll down, so that the search is only made over a tiny subset of all your likes.

## The solution

Because of the GDPR, Twitter lets users dowload an archive of all the data Twitter has about them. And the tweets each user liked is part of that information. To get this, one has to go to https://twitter.com/settings/your_twitter_data

The problem with that the list of liked tweets they give you when you ask for this info doesn't contain much info about each tweet: the beginning of the text and the Tweet ID. 

So, to enrich that, I made use of the Twitter API to make parallel calls and fetch all the info about all the tweets I had liked (over 6000!). For each Tweet, I get:
* Date
* Tweet
* User logo
* User alias
* Text
* Media
* User name
* Location
* User bio
* URL
* Likes
* RTs
* User follower count
* Logo user quoted tweet
* Quoted tweet text
* User alias quoted
* User name quoted
* ID

After that, I used Pandas to create a DataFrame containing all the tweets and save that information to a CSV.

Originally, I uploaded that CSV to Google Sheets. It's updated daily via an Integromat scenario. I chosed it because it works well enough and this is a small project. If I needed something that would deal with more data or required a lot of operations, I'd code it myself also to save money, but at this MVP stage, it's good enough.

And after taking this course, I created a Postgres DB on RDS to have the archive there and be able to make more advanced queries than in Google Sheets. 

## Data modeling
This is a project that doesn't involve heavy data engineering. The database has only one table, for my liked tweets, and is not normalized because the benefits of doing so don't outweight the downsides of having to do joins. Also, if I'm looking at the info about a tweet, I'll probably want to know all the data I have about it, so I'd have to rejoin the data at the end. 

This is the structure of the table. It could be fine-tuned but it works well enough now

         Column         |       Type        | Collation | Nullable | Default 
------------------------+-------------------+-----------+----------+---------
 date                   | character varying |           |          | 
 tweet                  | character varying |           |          | 
 user_logo              | character varying |           |          | 
 user_alias             | character varying |           |          | 
 text                   | character varying |           |          | 
 media                  | character varying |           |          | 
 user_name              | character varying |           |          | 
 location               | character varying |           |          | 
 user_bio               | character varying |           |          | 
 url                    | character varying |           |          | 
 likes                  | bigint            |           |          | 
 rts                    | bigint            |           |          | 
 user_follower_count    | bigint            |           |          | 
 logo_user_quoted_tweet | character varying |           |          | 
 quoted_tweet_text      | character varying |           |          | 
 user_alias_quoted      | character varying |           |          | 
 user_name_quoted       | character varying |           |          | 
 id                     | bigint            |           |          | 

## Addressing Other Scenarios

### What would I do if the data was increased by 100x.
I'd use a bigger Postgres machine or I'd run it on Redhift instead

### What would I do if the pipelines would be run on a daily basis by 7 am every day.
They already run daily, on Integromat. To do it with code I could run some code on AWS Lambda daily, a good old cronjob on an EC2 machine, create a pipeline in Airflow... I chose to keep it simpler in this case and solve the problem in the most efficient way, instead of using more complex tecnhologies just because

### The database needed to be accessed by 100+ people.
It can handle that without any problems, given the relatively small size of the data (<10k rows>). If that was a problem, I'd go for a bigger instance (it's running now on t2.micro instances, so there's room to go up from there)

# Execution
## Project code is clean and modular.
Yes. 

## Quality Checks
After making calls to the Twitter API, I assert in the code I'm actually getting more than 0 results, and also after copying the data to the DB (it was a one-shot task, so I checked that manually)

## Data Model
I provided the details for the single table that I'm using above. It's something simple, but I chose to solve real problem instead of going for an over-engineered solution in search of a problem.

## Datasets
I use the Twitter API as a data source, and then a CSV file is the source for the data that goes to the database.
There's no more than 1 million likes of data because I don't spend that much time on Twitter to have over a million fav tweets, fortunately :)