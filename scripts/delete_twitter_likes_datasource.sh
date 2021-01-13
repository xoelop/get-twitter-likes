source .env && curl \
  -H "Authorization: Bearer ${TINYBIRD_ADMIN_TOKEN}" \
  -X DELETE "https://api.tinybird.co/v0/datasources/twitter_likes"