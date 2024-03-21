import os
import sys


HOSTNAME_PLZ_CHANGE = "[HOSTNAME_PLZ_CHANGE]"
TITLE_PLZ_CHANGE = "[TITLE_PLZ_CHANGE]"
THEME_PLZ_CHANGE = "[THEME_PLZ_CHANGE]"
INFINITE_SCROLL_PLZ_CHANGE = "[INFINITE_SCROLL_PLZ_CHANGE]"

TEMPLATE="""[Server]
hostname = "[HOSTNAME_PLZ_CHANGE]"  # for generating links, change this to your own domain/ip
title = "[TITLE_PLZ_CHANGE]"
address = "0.0.0.0"
port = 8080
https = false  # disable to enable cookies when not using https
httpMaxConnections = 100
staticDir = "./public"

[Cache]
listMinutes = 240  # how long to cache list info (not the tweets, so keep it high)
rssMinutes = 10  # how long to cache rss queries
redisHost = "localhost"  # Change to "nitter-redis" if using docker-compose
redisPort = 6379
redisPassword = ""
redisConnections = 20  # minimum open connections in pool
redisMaxConnections = 30
# new connections are opened when none are available, but if the pool size
# goes above this, they're closed when released. don't worry about this unless
# you receive tons of requests per second

[Config]
hmacKey = "secretkey"  # random key for cryptographic signing of video urls
base64Media = false  # use base64 encoding for proxied media urls
enableRSS = true  # set this to false to disable RSS feeds
enableDebug = false  # enable request logs and debug endpoints (/.accounts)
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

def main() -> str:
    # hostname
    hostname = "localhost:8080"
    if os.getenv("FLY_APP_NAME"):
        hostname = f"{os.getenv('FLY_APP_NAME')}.fly.dev"
    
    # other customizations
    title = os.getenv("INSTANCE_TITLE", "My Nitter instance")
    theme = os.getenv("INSTANCE_THEME", "Nitter")
    infinite_scroll = "true" if os.getenv("INSTANCE_INFINITE_SCROLL") == "1" else "false"

    return TEMPLATE \
        .replace(HOSTNAME_PLZ_CHANGE, hostname) \
        .replace(TITLE_PLZ_CHANGE, title) \
        .replace(THEME_PLZ_CHANGE, theme) \
        .replace(INFINITE_SCROLL_PLZ_CHANGE, infinite_scroll)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 gen_nitter_conf.py <output_file>")
        sys.exit(1)

    output_file = sys.argv[1]
    with open(output_file, "w") as f:
        f.write(main())