source .env && \
curl \
  -H "Authorization: Bearer ${TINYBIRD_ADMIN_TOKEN}" \
  -X POST 'https://api.tinybird.co/v0/datasources?name=twitter_likes' \
  -d 'schema=
    `date` DateTime, 
    `link` String, 
    `user_logo` String, 
    `screenname` String, 
    `tweet_text` String, 
    `text` String, 
    `media` Nullable(String), 
    `username` String, 
    `location` Nullable(String), 
    `bio` Nullable(String), 
    `url` Nullable(String), 
    `title` Nullable(String), 
    `description` Nullable(String), 
    `likes` UInt32, 
    `rts` UInt32, 
    `num_followers` UInt32, 
    `quoted_status_id` Nullable(UInt64), 
    `id` UInt64, 
    `insert_date` DateTime
  ' \
  -d "engine=ReplacingMergeTree" \
  -d "engine_sorting_key=id" \
  -d "engine_ver=insert_date"