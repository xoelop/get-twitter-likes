source .env && curl \
  -F "csv=@data/likes2.csv" \
  -H "Authorization: Bearer ${TINYBIRD_ADMIN_TOKEN}" \
  -X POST 'https://api.tinybird.co/v0/datasources?name=twitter_likes&mode=replace'