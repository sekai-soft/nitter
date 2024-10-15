#!/bin/bash
set -e

echo Dumping auth env...
echo TWITTER_USERNAME=$TWITTER_USERNAME > /src/.env
echo TWITTER_PASSWORD=$TWITTER_PASSWORD >> /src/.env
echo TWITTER_CREDENTIALS_FILE=$TWITTER_CREDENTIALS_FILE >> /src/.env
echo RESET_NITTER_ACCOUNTS_FILE=$RESET_NITTER_ACCOUNTS_FILE >> /src/.env
echo DEBUG=$DEBUG >> /src/.env

echo Dumping custom path env...
echo NITTER_ACCOUNTS_FILE=$NITTER_ACCOUNTS_FILE >> /src/.env

echo Dumping redis connection env...
echo REDIS_HOST=$REDIS_HOST >> /src/.env
echo REDIS_PORT=$REDIS_PORT >> /src/.env
echo REDIS_PASSWORD=$REDIS_PASSWORD >> /src/.env

echo Dumping instance customization env...
echo INSTANCE_PORT=$INSTANCE_PORT >> /src/.env
echo INSTANCE_HTTPS=$INSTANCE_HTTPS >> /src/.env
echo FLY_APP_NAME=$FLY_APP_NAME >> /src/.env
echo INSTANCE_HOSTNAME=$INSTANCE_HOSTNAME >> /src/.env
echo INSTANCE_BASE64_MEDIA=$INSTANCE_BASE64_MEDIA >> /src/.env
echo INSTANCE_TITLE=$INSTANCE_TITLE >> /src/.env
echo INSTANCE_THEME=$INSTANCE_THEME >> /src/.env
echo INSTANCE_INFINITE_SCROLL=$INSTANCE_INFINITE_SCROLL >> /src/.env
echo INSTANCE_ENABLE_DEBUG=$INSTANCE_ENABLE_DEBUG >> /src/.env

echo Dumping instance guardian env...
echo INSTANCE_RSS_PASSWORD=$INSTANCE_RSS_PASSWORD >> /src/.env
echo INSTANCE_WEB_USERNAME=$INSTANCE_WEB_USERNAME >> /src/.env
echo INSTANCE_WEB_PASSWORD=$INSTANCE_WEB_PASSWORD >> /src/.env

echo Writing Procfile...

echo "web: /src/scripts/nitter.sh" > /src/Procfile

if [ "$DISABLE_REDIS" != "1" ]; then
  echo "redis: /src/scripts/redis.sh" >> /src/Procfile
fi
echo DISABLE_REDIS=$DISABLE_REDIS >> /src/.env

if [ "$DISABLE_NGINX" != "1" ]; then
  echo "nginx: /src/scripts/nginx.sh" >> /src/Procfile
fi
