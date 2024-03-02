import random
import string
import requests
import time
import signal
import sys
import os

base_url = "https://api.mail.tm"

def get_random_string(length, chars):
    return "".join(random.choices(chars, k=length))

def get_api_response(url, headers, params=None):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code < 400:
        return response
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

def get_api_json(url, headers, params=None):
    response = get_api_response(url, headers, params)
    return response.json()

def get_domains(headers):
    url = base_url + "/domains"
    return get_api_json(url, headers)

def get_account_token(headers, domain, username, password):
    url = base_url + "/token"
    headers["content-type"] = "application/json"
    body = {"address": f"{username}@{domain}", "password": password}
    response = requests.post(url, headers=headers, json=body)
    if response.status_code < 400:
        return response.json()
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

def get_account_messages(headers):
    url = base_url + "/messages"
    return get_api_json(url, headers)

def get_message(headers, message_id):
    url = base_url + f"/messages/{message_id}"
    return get_api_json(url, headers)

def get_email_address():
    headers = {
        "accept": "application/ld+json",
        "content-type": "application/json",
    }
    data = get_domains(headers)
    domain = random.choice(data["hydra:member"])["domain"]
    username_length = 10
    password_length = 15
    username_chars = string.ascii_lowercase + string.digits
    password_chars = string.ascii_letters + string.digits + string.punctuation
    username = get_random_string(username_length, username_chars)
    password = get_random_string(password_length, password_chars)
    headers["content-type"] = "application/json"
    body = {"address": f"{username}@{domain}", "password": password}
    response = requests.post(base_url + "/accounts", headers=headers, json=body)
    if response.status_code < 400:
        data = response.json()
        account_id = data["id"]
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")
    data = get_account_token(headers, domain, username, password)
    token = data["token"]
    return username + "@" + domain, password, token

def check_messages(headers):
    data = get_account_messages(headers)
    messages = data["hydra:member"]
    print(f"Number of messages: {len(messages)}")
    for message in messages:
        message_id = message["id"]
        message_subject = message["subject"]
        message_from = message["from"]["address"]
        print(f"Message ID: {message_id}")
        print(f"Message Subject: {message_subject}")
        print(f"Message From: {message_from}")
        data = get_message(headers, message_id)
        message_text = data["text"]
        print(f"Message Text: {message_text}")

def exit_program(signal_number, frame):
    print("Program terminated by user")
    sys.exit(0)

def main():
    import requests

    signal.signal(signal.SIGINT, exit_program)

    headers = {
        "accept": "application/ld+json",
        "content-type": "application/json",
    }

    try:
        data = get_domains(headers)
    except Exception as e:
        print(f"Error: {e}")
        return

    domain = data["hydra:member"][0]["domain"]

    print(f"Domain: {domain}")

    username_length = 10
    password_length = 15

    username_chars = string.ascii_lowercase + string.digits
    password_chars = string.ascii_letters + string.digits + string.punctuation

    username = get_random_string(username_length, username_chars)
    password = get_random_string(password_length, password_chars)

    print(f"Username: {username}")
    print(f"Password: {password}")

    try:
        headers["content-type"] = "application/json"
        body = {"address": f"{username}@{domain}", "password": password}
        response = requests.post(base_url + "/accounts", headers=headers, json=body)
        if response.status_code < 400:
            data = response.json()
            account_id = data["id"]
            print(f"Account ID: {account_id}")
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
        return

    try:
        data = get_account_token(headers, domain, username, password)
    except Exception as e:
        print(f"Error: {e}")
        return

    token = data["token"]

    print(f"Token: {token}")

    headers["authorization"] = f"Bearer {token}"

    refresh_interval = 5
    refresh_countdown = refresh_interval

    while True:
        try:
            if refresh_countdown == 0:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"Email address: {username}@{domain}")
                check_messages(headers)
                refresh_countdown = refresh_interval
            else:
                print(f"Refreshing in {refresh_countdown} seconds", end="\r")
                refresh_countdown -= 1
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()
