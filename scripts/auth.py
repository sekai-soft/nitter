# adapted from
# https://github.com/zedeus/nitter/issues/983#issuecomment-1914616663
import requests
import base64
import json
import sys
import os
import logging
from typing import Optional


logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG if os.getenv("DEBUG") == "1" else logging.INFO)


TW_CONSUMER_KEY = '3nVuSoBZnx6U4vzUxf5w'
TW_CONSUMER_SECRET = 'Bcs59EFbbsdF6Sl9Ng71smgStWEGwXXKSjYvPVt7qys'
TW_ANDROID_BASIC_TOKEN = 'Basic {token}'.format(token=base64.b64encode(
    (TW_CONSUMER_KEY + ":" + TW_CONSUMER_SECRET).encode()
).decode())
logging.debug("TW_ANDROID_BASIC_TOKEN=" + TW_ANDROID_BASIC_TOKEN)


def auth(username: str, password: str, mfa_code: Optional[str]) -> Optional[dict]:
    logging.debug(f"start authenticating @{username}")

    bearer_token_req = requests.post("https://api.twitter.com/oauth2/token",
        headers={
            'Authorization': TW_ANDROID_BASIC_TOKEN,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data='grant_type=client_credentials'
    ).json()
    bearer_token = ' '.join(str(x) for x in bearer_token_req.values())
    logging.debug("bearer_token=" + bearer_token)

    guest_token = requests.post("https://api.twitter.com/1.1/guest/activate.json", headers={
        'Authorization': bearer_token,
    }).json()['guest_token']
    logging.debug("guest_token=" + guest_token)

    twitter_header = {
        'Authorization': bearer_token,
        "Content-Type": "application/json",
        "User-Agent": "TwitterAndroid/10.21.0-release.0 (310210000-r-0) ONEPLUS+A3010/9 (OnePlus;ONEPLUS+A3010;OnePlus;OnePlus3;0;;1;2016)",
        "X-Twitter-API-Version": '5',
        "X-Twitter-Client": "TwitterAndroid",
        "X-Twitter-Client-Version": "10.21.0-release.0",
        "OS-Version": "28",
        "System-User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ONEPLUS A3010 Build/PKQ1.181203.001)",
        "X-Twitter-Active-User": "yes",
        "X-Guest-Token": guest_token,
        "X-Twitter-Client-DeviceID": ""
    }

    session = requests.Session()

    task1 = session.post('https://api.twitter.com/1.1/onboarding/task.json',
        params={
            'flow_name': 'login',
            'api_version': '1',
            'known_device_token': '',
            'sim_country_code': 'us'
        },
        json={
            "flow_token": None,
            "input_flow_data": {
                "country_code": None,
                "flow_context": {
                    "referrer_context": {
                        "referral_details": "utm_source=google-play&utm_medium=organic",
                        "referrer_url": ""
                    },
                    "start_location": {
                        "location": "deeplink"
                    }
                },
                "requested_variant": None,
                "target_user_id": 0
            }
        },
        headers=twitter_header
    )
    logging.debug("task1 res=" + str(task1.json()))

    session.headers['att'] = task1.headers.get('att')
    task2 = session.post('https://api.twitter.com/1.1/onboarding/task.json', 
        json={
            "flow_token": task1.json().get('flow_token'),
            "subtask_inputs": [{
                    "enter_text": {
                        "suggestion_id": None,
                        "text": username,
                        "link": "next_link"
                    },
                    "subtask_id": "LoginEnterUserIdentifier"
                }
            ]
        },
        headers=twitter_header
    )
    logging.debug("task2 res=" + str(task2.json()))

    task3 = session.post('https://api.twitter.com/1.1/onboarding/task.json', 
        json={
            "flow_token": task2.json().get('flow_token'),
            "subtask_inputs": [{
                    "enter_password": {
                        "password": password,
                        "link": "next_link"
                    },
                    "subtask_id": "LoginEnterPassword"
                }
            ],
        },
        headers=twitter_header
    )
    logging.debug("task3 res=" + str(task3.json()))

    for t3_subtask in task3.json().get('subtasks', []):
        if "open_account" in t3_subtask:
            return t3_subtask["open_account"]
        elif "enter_text" in t3_subtask:
            response_text = t3_subtask["enter_text"]["hint_text"]
            task4 = session.post(
                "https://api.twitter.com/1.1/onboarding/task.json",
                json={
                    "flow_token": task3.json().get("flow_token"),
                    "subtask_inputs": [
                        {
                            "enter_text": {
                                "suggestion_id": None,
                                "text": mfa_code,
                                "link": "next_link",
                            },
                            # was previously LoginAcid
                            "subtask_id": "LoginTwoFactorAuthChallenge",
                        }
                    ],
                },
                headers=twitter_header,
            ).json()
            logging.debug("task4 res=" + str(task4))
            for t4_subtask in task4.get("subtasks", []):
                if "open_account" in t4_subtask:
                    return t4_subtask["open_account"]

    return None


def parse_auth_file(auth_file: str) -> bool:
    try:
        with open(auth_file, "r") as f:
            res = json.loads(f.read())
    except json.JSONDecodeError:
        logging.error(f"Auth file is not a valid json file")
        return False
    if isinstance(res, dict):
        logging.error(f"Expecting auth file to be a json list")
        return False
    if len(res) == 0:
        logging.error(f"Expecting auth file to be non-empty")
        return False
    for i, r in enumerate(res):
        if "oauth_token" not in r:
            logging.error(f"Expecting 'oauth_token' in auth item #{i + 1}")
            return False
        if "oauth_token_secret" not in r:
            logging.error(f"Expecting 'oauth_token_secret' in auth item #{i + 1}")
            return False
    logging.debug(f"There are {len(res)} accounts")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 auth.py <output_file>")
        sys.exit(1)

    output_file = sys.argv[1]

    if os.getenv("RESET_NITTER_ACCOUNTS_FILE", "0") == "1" and os.path.exists(output_file):
        print(f"Resetting auth file {output_file}")
        os.remove(output_file)

    if os.path.exists(output_file):
        print(f"Validating auth file {output_file}")
        if parse_auth_file(output_file):
            print(f"Auth file {output_file} is valid")
            sys.exit(0)
        else:
            print(f"Auth file {output_file} is invalid. Please remove and rerun.")
            sys.exit(1)

    twitter_credentials_file = os.getenv("TWITTER_CREDENTIALS_FILE", None)
    username = os.getenv("TWITTER_USERNAME", None)
    password = os.getenv("TWITTER_PASSWORD", None)

    if not twitter_credentials_file and not (username and password):
        print("Please set environment variable TWITTER_CREDENTIALS_FILE, or both TWITTER_USERNAME and TWITTER_PASSWORD")
        sys.exit(1)

    twitter_credentials = []
    if twitter_credentials_file:
        with open(twitter_credentials_file, "r") as f:
            twitter_credentials = json.loads(f.read())
    else:
        mfa_code = os.getenv("TWITTER_MFA_CODE", None)
        twitter_credentials = [{"username": username, "password": password, "mfa_code": mfa_code}]

    auth_results = []
    for credential in twitter_credentials:
        username = credential["username"]
        password = credential["password"]
        mfa_code = credential.get("mfa_code", None)
        auth_result = auth(username, password, mfa_code)
        auth_results.append(auth_result)

    if len(list(filter(lambda x: x is not None, auth_results))) == 0:
        print("Failed authentication for any account. Did you enter the right username/password? Please rerun with environment variable DEBUG=1 for debugging, e.g. uncomment the DEBUG=1 in docker-compose.yml file.")
        sys.exit(1)

    valid_auth_results = []
    for i, auth_result in enumerate(auth_results):
        if auth_result is None:
            print(f"Failed authentication for account #{i}, but still proceeding.")
        else:
            valid_auth_results.append(auth_result)

    with open(output_file, "w") as f:
        f.write(json.dumps(valid_auth_results))
    print(f"Auth file {output_file} created successfully")
