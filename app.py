#!/bin/python3

import requests
import os
import signal
import sys
import html
import json
import random
import time


# Chars required to be escaped by Telegram Bot API
# https://core.telegram.org/bots/api#formatting-options
ESCAPE_CHARS = set(["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"])

DATA_FILE_PATH = "/data/data.json"
TELEGRAM_BOT_TOKEN = None
TELEGRAM_CHAT_ID = None
BATCH_SIZE = 1
MIN_INTERVAL = 1440
MAX_INTERVAL = 1440


# Function to get the latest XKCD comic number
def get_latest_comic_num():
    response = requests.get("https://xkcd.com/info.0.json")
    response.raise_for_status()
    return response.json()["num"]

# Function to get a specific XKCD comic by number
def get_comic(num):
    url = f"https://xkcd.com/{num}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Function to send a message through the Telegram bot
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": escape_string(text),
        "parse_mode": "MarkdownV2"
    }
    response = requests.post(url, data=data)
    response.raise_for_status()

def send_telegram_photo(text, img_url):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": img_url,
        "caption": text,
        "parse_mode": "MarkdownV2"
    }
    response = requests.post(url, data=data)
    response.raise_for_status()

def escape_string(s):
    return "".join(["\\" + c if c in ESCAPE_CHARS else c for c in s])

def generate_msg(comic):
    url = f"https://xkcd.com/{comic['num']}/"
    msg = f"[__*{comic['num']}\. {escape_string(html.unescape(comic['title']))}*__]({url})\n\n" \
            + f"{escape_string(html.unescape(comic['alt']))}"

    if "link" in comic and comic["link"]:
        msg += f"\n\n[Link]({comic['link']})"
    if "extra_parts" in comic and comic["extra_parts"]:
        msg += f"\n\n{escape_string(html.unescape(comic['extra_parts']))}"

    return msg

# Function to send a random XKCD comic to Telegram
def send_random_xkcd_to_telegram():
    try:
        # First get the latest comic num
        retry_times = 3
        while retry_times > 0:
            try:
                latest_comic_num = get_latest_comic_num()
                break

            except Exception as e:
                retry_times -= 1
                if retry_times <= 0:
                    raise e

        # Get an unvisited number
        if os.path.exists(DATA_FILE_PATH):
            with open(DATA_FILE_PATH, "r") as f:
                stored_data = json.load(f)
        else:
            stored_data = {
                "visited": []
            }

        # Check if every comic is visited and need to start over
        if len(stored_data["visited"]) == latest_comic_num:
            send_telegram_message("[xkcd Random Bot] Finally, we have exhausted the comics. Let's start over!")
            stored_data["visited"] = []

        unvisited_pages = list(set(range(1, latest_comic_num + 1)) - set(stored_data["visited"]))

        random_comic_num = random.choice(unvisited_pages)

        print(f"Fetching comic {random_comic_num} ...")

        retry_times = 3
        while retry_times > 0:
            try:
                # Handle comic #404 (it's an actual 404 not found page)
                if random_comic_num == 404:
                    comic = {
                        "num": 404,
                        "alt": "404 Not Found",
                        "img": "https://xkcd.com/s/0b7742.png",
                        "title": "404",
                        "safe_title": "404"
                    }
                    break

                comic = get_comic(random_comic_num)

                break

            except Exception as e:
                retry_times -= 1
                if retry_times <= 0:
                    raise e

        message_text = generate_msg(comic)
        send_telegram_photo(message_text, comic["img"])
        
        stored_data["visited"].append(random_comic_num)

        with open(DATA_FILE_PATH, "w") as f:
            json.dump(stored_data, f)

    except Exception as e:
        send_telegram_message(f"[xkcd Random Bot] [🔴 Down] Error encountered: {e}")
        raise e

def main():
    global TELEGRAM_BOT_TOKEN
    global TELEGRAM_CHAT_ID
    global BATCH_SIZE
    global MIN_INTERVAL
    global MAX_INTERVAL

    # Your Telegram Bot's API Token and Chat ID
    TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
    TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
    if "BATCH_SIZE" in os.environ:
        BATCH_SIZE = int(os.environ["BATCH_SIZE"])
    if "MIN_INTERVAL" in os.environ:
        MIN_INTERVAL = int(os.environ["MIN_INTERVAL"])
    if "MAX_INTERVAL" in os.environ:
        MAX_INTERVAL = int(os.environ["MAX_INTERVAL"])

    if BATCH_SIZE < 0:
        err_msg = f"[xkcd Random Bot] [🔴 Error] Invalid batch size {BATCH_SIZE}"
        send_telegram_message(err_msg)
        raise Exception(err_msg)
    
    if MIN_INTERVAL > MAX_INTERVAL or MIN_INTERVAL <= 0:
        err_msg = f"[xkcd Random Bot] [🔴 Error] Invalid intervals: {MIN_INTERVAL}, {MAX_INTERVAL}"
        send_telegram_message(err_msg)
        raise Exception(err_msg)

    def handler(sig, frame):
        print("Shutting down ...", file=sys.stderr)
        send_telegram_message(f"[xkcd Random Bot] [🔴 Down] Shuting down by SIGINT/SIGTERM ..")
        exit(0)

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    send_telegram_message("[xkcd Random Bot] [✅ Up] Running")

    while True:
        # Send comic(s), then sleep
        for _ in range(BATCH_SIZE):
            send_random_xkcd_to_telegram()

        time.sleep(random.randint(MIN_INTERVAL, MAX_INTERVAL) * 60)

if __name__ == "__main__":
    main()
