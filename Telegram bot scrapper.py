import os
import time
import requests
import pandas as pd
import json
from bs4 import BeautifulSoup

# -----------------------
# ENV LOAD (AUTO DETECT)
# -----------------------
def load_env():
    paths = [".env", "/storage/emulated/0/.env"]
    env = {}

    for p in paths:
        if os.path.exists(p):
            print(f".env loaded from: {p}")
            with open(p) as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        env[k] = v
            return env

    raise Exception("No .env file found!")

env = load_env()

BOT_TOKEN = env.get("BOT_TOKEN")
CHAT_ID = env.get("CHAT_ID")

# -----------------------
# GLOBALS
# -----------------------
REQUEST_FILE = "request.txt"
processed_urls = set()
data_store = []
last_update_id = None

# -----------------------
# MESSAGE SYSTEM
# -----------------------
def send_message(msg):
    print(msg)
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("Telegram error")

# -----------------------
# UI
# -----------------------
def welcome():
    print("\n" + "="*40)
    print("🔥 Welcome Sam Bhai / Rolex Sir 🔥")
    print("Smart Scraper System Ready 🚀")
    print("="*40)

def menu():
    print("\n📌 Kya karna hai:")
    print("1 → request.txt scrape")
    print("2 → manual URL")
    print("3 → Telegram mode")
    print("exit → band karo")

# -----------------------
# TELEGRAM RECEIVE
# -----------------------
def get_updates():
    global last_update_id

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

    if last_update_id:
        url += f"?offset={last_update_id + 1}"

    try:
        res = requests.get(url).json()

        for upd in res.get("result", []):
            last_update_id = upd["update_id"]
            if "message" in upd:
                return upd["message"].get("text", "")
    except:
        pass

    return None

# -----------------------
# URL FIX
# -----------------------
def fix_url(url):
    if not url.startswith("http"):
        return "https://" + url
    return url

# -----------------------
# FETCH
# -----------------------
def fetch(url):
    send_message("🌐 Server ko request bhej rahe hain...")

    try:
        r = requests.get(url, timeout=5)

        if r.status_code != 200:
            send_message("❌ Request fail")
            return None, None

        if "application/json" in r.headers.get("Content-Type", ""):
            send_message("📦 Rolex sir, JSON mila")
            return r.json(), "json"

        else:
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.title.string.strip() if soup.title else "No Title"
            send_message("📄 Rolex sir, HTML mila")
            return {"url": url, "title": title}, "html"

    except:
        send_message("❌ Fetch error")
        return None, None

# -----------------------
# SAVE
# -----------------------
def save(data, dtype):
    global data_store

    if not data:
        send_message("⚠️ Save skip")
        return

    send_message("📦 Data process ho raha hai...")

    data_store.append(data)

    # JSON
    with open("output.json", "w") as f:
        json.dump(data_store, f, indent=2)
    send_message("📁 JSON update")

    # CSV
    df = pd.DataFrame(data_store)
    df.drop_duplicates(inplace=True)
    df.to_csv("output.csv", index=False)
    send_message("📊 CSV update")

    send_message(f"✅ {dtype.upper()} process complete")

# -----------------------
# PROCESS
# -----------------------
def process_url(url):
    url = fix_url(url)

    if not url or url in processed_urls:
        return

    send_message(f"\n🔗 URL: {url}")
    send_message("⏳ Processing start (5-10 sec lag sakta hai)")

    data, dtype = fetch(url)

    if data:
        save(data, dtype)
    else:
        send_message("❌ Data nahi mila")

    processed_urls.add(url)

    send_message("🔒 Task complete, next input ka wait...")

# -----------------------
# TXT
# -----------------------
def process_txt():
    if not os.path.exists(REQUEST_FILE):
        send_message("❌ request.txt nahi mila")
        return

    with open(REQUEST_FILE) as f:
        urls = [u.strip() for u in f if u.strip()]

    for u in urls:
        process_url(u)

# -----------------------
# TELEGRAM MODE
# -----------------------
def telegram_mode():
    send_message("📡 Telegram mode ON")

    while True:
        msg = get_updates()

        if msg:
            if msg.lower() in ["exit", "stop"]:
                send_message("❌ Telegram mode OFF")
                break

            if "." in msg:
                process_url(msg)

        time.sleep(2)

# -----------------------
# MAIN
# -----------------------
def main():
    welcome()
    send_message("🚀 System ready Sam Bhai")

    while True:
        menu()
        ch = input("Enter: ").strip().lower()

        if ch in ["exit", "q"]:
            send_message("👋 System band")
            break

        elif ch == "1":
            process_txt()

        elif ch == "2":
            url = input("URL daalo: ")
            process_url(url)

        elif ch == "3":
            telegram_mode()

        else:
            print("Invalid choice")

# -----------------------
# RUN
# -----------------------
if __name__ == "__main__":
    main()
