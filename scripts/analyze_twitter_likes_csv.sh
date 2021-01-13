source .env && curl \
  -F "csv=@data/latest_likes.csv" \
  -H "Authorization: Bearer ${TINYBIRD_ADMIN_TOKEN}" \
  -X POST 'https://api.tinybird.co/v0/datasources?name=twitter_likes1&mode=append&dry=true' 