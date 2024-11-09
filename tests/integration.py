import os
import time
import requests

# Stop and start the docker compose stack
os.system("docker compose -f docker-compose.yml down")
os.system("docker compose -f docker-compose.yml up --build -d")

# Long poll (max 5 minutes) localhost:8081 until it returns 401
root_url = "http://localhost:8081"
long_poll_timeout = 5 * 60  # 5 minutes in seconds
long_poll_interval = 5  # Interval between requests in seconds
long_poll_start_time = time.time()

while time.time() - long_poll_start_time < long_poll_timeout:
    try:
        print(f"Polling {root_url} for 401")
        long_poll_resp = requests.get(root_url)
        if long_poll_resp.status_code == 401:
            print("Received 401")
            break
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    
    time.sleep(long_poll_interval)
else:
    print("Timeout reached without receiving 401")

# Test RSS feed unauthenticated. Should return 200 but empty body.
print("Testing RSS feed unauthenticated")
unauthenticated_rss_url = f"{root_url}/elonmusk/rss"
unauthenticated_rss_resp = requests.get(unauthenticated_rss_url)
assert unauthenticated_rss_resp.status_code == 200
assert unauthenticated_rss_resp.text == ""

# Get RSS key from .env file
with open(".env") as f:
    for line in f:
        if line.startswith("INSTANCE_RSS_PASSWORD"):
            rss_key = line.split("=")[1].strip()

# Test RSS feed authenticated. Should return 200 with non-empty body.
print("Testing RSS feed authenticated")
authenticated_rss_url = f"{root_url}/elonmusk/rss?key={rss_key}"
authenticated_rss_resp = requests.get(authenticated_rss_url)
assert authenticated_rss_resp.status_code == 200
assert authenticated_rss_resp.text != ""

# Test web UI unauthenticated. Should return 401.
print("Testing web UI unauthenticated")
web_ui_url = f"{root_url}/elonmusk"
unauthenticated_web_ui_resp = requests.get(web_ui_url)
assert unauthenticated_web_ui_resp.status_code == 401

# Get web UI username and password from .env file
with open(".env") as f:
    for line in f:
        if line.startswith("INSTANCE_WEB_USERNAME"):
            username = line.split("=")[1].strip()
        elif line.startswith("INSTANCE_WEB_PASSWORD"):
            password = line.split("=")[1].strip()

# Test web UI authenticated. Should return 200 with non-empty body.
print("Testing web UI authenticated")
authenticated_web_ui_resp = requests.get(web_ui_url, auth=(username, password))
assert authenticated_web_ui_resp.status_code == 200
assert authenticated_web_ui_resp.text != ""

# Export logs
os.system("docker compose -f docker-compose.yml logs > integration-test.logs")

# Stop the docker compose stack
os.system("docker compose -f docker-compose.yml down")
