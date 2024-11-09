import os
import sys


HOSTNAME_PLZ_CHANGE = "[HOSTNAME_PLZ_CHANGE]"
TITLE_PLZ_CHANGE = "[TITLE_PLZ_CHANGE]"
PORT_PLZ_CHANGE = "[PORT_PLZ_CHANGE]"
HTTPS_PLZ_CHANGE = "[HTTPS_PLZ_CHANGE]"
REDIS_HOST_PLZ_CHANGE = "[REDIS_HOST_PLZ_CHANGE]"
REDIS_PORT_PLZ_CHANGE = "[REDIS_PORT_PLZ_CHANGE]"
REDIS_PASSWORD_PLZ_CHANGE = "[REDIS_PASSWORD_PLZ_CHANGE]"
BASE64_MEDIA_PLZ_CHANGE = "[BASE64_MEDIA_PLZ_CHANGE]"
THEME_PLZ_CHANGE = "[THEME_PLZ_CHANGE]"
INFINITE_SCROLL_PLZ_CHANGE = "[INFINITE_SCROLL_PLZ_CHANGE]"
ENABLE_DEBUG_PLZ_CHANGE = "[ENABLE_DEBUG_PLZ_CHANGE]"
RSS_MIUNTES_PLZ_CHANGE = "[RSS_MIUNTES_PLZ_CHANGE]"

TEMPLATE = """[Server]
hostname = "[HOSTNAME_PLZ_CHANGE]"  # for generating links, change this to your own domain/ip
title = "[TITLE_PLZ_CHANGE]"
address = "0.0.0.0"
port = [PORT_PLZ_CHANGE]
https = [HTTPS_PLZ_CHANGE]  # disable to enable cookies when not using https
httpMaxConnections = 100
staticDir = "./public"

[Cache]
listMinutes = 240  # how long to cache list info (not the tweets, so keep it high)
rssMinutes = [RSS_MIUNTES_PLZ_CHANGE]  # how long to cache rss queries
redisHost = "[REDIS_HOST_PLZ_CHANGE]"  # Change to "nitter-redis" if using docker-compose
redisPort = [REDIS_PORT_PLZ_CHANGE]
redisPassword = "[REDIS_PASSWORD_PLZ_CHANGE]"
redisConnections = 20  # minimum open connections in pool
redisMaxConnections = 30
# new connections are opened when none are available, but if the pool size
# goes above this, they're closed when released. don't worry about this unless
# you receive tons of requests per second

[Config]
hmacKey = "secretkey"  # random key for cryptographic signing of video urls
base64Media = [BASE64_MEDIA_PLZ_CHANGE]  # use base64 encoding for proxied media urls
enableRSS = true  # set this to false to disable RSS feeds
enableDebug = [ENABLE_DEBUG_PLZ_CHANGE]  # enable request logs and debug endpoints (/.accounts)
proxy = ""  # http/https url, SOCKS proxies are not supported
proxyAuth = ""
tokenCount = 10
# minimum amount of usable tokens. tokens are used to authorize API requests,
# but they expire after ~1 hour, and have a limit of 500 requests per endpoint.
# the limits reset every 15 minutes, and the pool is filled up so there's
# always at least `tokenCount` usable tokens. only increase this if you receive
# major bursts all the time and don't have a rate limiting setup via e.g. nginx

# Change default preferences here, see src/prefs_impl.nim for a complete list
[Preferences]
theme = "[THEME_PLZ_CHANGE]"
replaceTwitter = ""
replaceYouTube = ""
replaceReddit = ""
proxyVideos = true
hlsPlayback = false
infiniteScroll = [INFINITE_SCROLL_PLZ_CHANGE]
"""


def getenv_treat_empty_string_as_none(key: str, default: str) -> str:
    value = os.getenv(key)
    if not value:
        return default
    return value


def main() -> str:
    # port
    port = getenv_treat_empty_string_as_none("INSTANCE_PORT", "8080")

    # hostname
    hostname = f"localhost:{port}"
    if os.getenv("FLY_APP_NAME"):
        hostname = f"{os.getenv('FLY_APP_NAME')}.fly.dev"
    elif os.getenv("INSTANCE_HOSTNAME"):
        hostname = os.getenv("INSTANCE_HOSTNAME")
    
    # redis connection info
    redis_host = getenv_treat_empty_string_as_none("REDIS_HOST", "localhost")
    redis_port = getenv_treat_empty_string_as_none("REDIS_PORT", "6379")
    redis_password = getenv_treat_empty_string_as_none("REDIS_PASSWORD", "")

    # other customizations
    https = "true" if os.getenv("INSTANCE_HTTPS") == "1" else "false"
    base64_media = "true" if os.getenv("INSTANCE_BASE64_MEDIA") == "1" else "false"
    title = getenv_treat_empty_string_as_none("INSTANCE_TITLE", "My Nitter instance")
    theme = getenv_treat_empty_string_as_none("INSTANCE_THEME", "Nitter")
    infinite_scroll = "true" if os.getenv("INSTANCE_INFINITE_SCROLL") == "1" else "false"
    enable_debug = "true" if os.getenv("INSTANCE_ENABLE_DEBUG") == "1" else "false"
    rss_minutes = getenv_treat_empty_string_as_none("INSTANCE_RSS_MINUTES", "10")

    return TEMPLATE \
        .replace(HOSTNAME_PLZ_CHANGE, hostname) \
        .replace(PORT_PLZ_CHANGE, port) \
        .replace(HTTPS_PLZ_CHANGE, https) \
        .replace(REDIS_HOST_PLZ_CHANGE, redis_host) \
        .replace(REDIS_PORT_PLZ_CHANGE, redis_port) \
        .replace(REDIS_PASSWORD_PLZ_CHANGE, redis_password) \
        .replace(BASE64_MEDIA_PLZ_CHANGE, base64_media) \
        .replace(TITLE_PLZ_CHANGE, title) \
        .replace(THEME_PLZ_CHANGE, theme) \
        .replace(INFINITE_SCROLL_PLZ_CHANGE, infinite_scroll) \
        .replace(ENABLE_DEBUG_PLZ_CHANGE, enable_debug) \
        .replace(RSS_MIUNTES_PLZ_CHANGE, rss_minutes)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 gen_nitter_conf.py <output_file>")
        sys.exit(1)

    output_file = sys.argv[1]
    with open(output_file, "w") as f:
        f.write(main())
