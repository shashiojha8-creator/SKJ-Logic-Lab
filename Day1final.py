import os
import time
import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
import logging
from datetime import datetime

# -----------------------
# LOGGING SETUP
# -----------------------
log_file = "scraper.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%H:%M:%S")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# -----------------------
# HEADERS (HTML only)
# -----------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# -----------------------
# ENV LOAD
# -----------------------
def load_env():
    paths = [".env", "/storage/emulated/0/.env"]
    env = {}
    for p in paths:
        if os.path.exists(p):
            logging.info(f".env loaded from: {p}")
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
PROCESSED_FILE = "processed_urls.txt"
processed_urls = set()
data_store = []
last_update_id = None

# Load processed URLs from file
if os.path.exists(PROCESSED_FILE):
    with open(PROCESSED_FILE) as f:
        processed_urls = set(u.strip() for u in f if u.strip())

# -----------------------
# MESSAGE SYSTEM
# -----------------------
def send_message(msg):
    logging.info(msg)
    try:
        if BOT_TOKEN and CHAT_ID:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        logging.warning(f"Telegram message failed: {e}")

# -----------------------
# UI
# -----------------------
def welcome():
    print("\n" + "="*50)
    print("🔥 Welcome Sam Bhai / Rolex Sir 🔥")
    print("Smart Scraper System Ready 🚀")
    print("="*50)

def menu():
    print("\n📌 Kya karna hai:")
    print("1 → request.txt scrape (auto/manual)")
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
        res = requests.get(url, timeout=10).json()
        for upd in res.get("result", []):
            last_update_id = upd["update_id"]
            if "message" in upd:
                return upd["message"].get("text", "")
    except Exception as e:
        logging.warning(f"Telegram get_updates failed: {e}")
    return None

# -----------------------
# URL FIX
# -----------------------
def fix_url(url):
    if not url.startswith("http"):
        return "https://" + url
    return url

# -----------------------
# AUTO CLASS GUESS
# -----------------------
def guess_classes(soup):
    authors = soup.find_all("small")
    quotes = soup.find_all("span")
    return authors, quotes

# -----------------------
# FETCH WITH RETRY + ESTIMATED MSG
# -----------------------
def fetch(url, mode="manual", author_class=None, quote_class=None, retries=3):
    send_message(f"Rolex bhai 🌐 Request bhej rahe hain: {url}")
    attempt = 0

    while attempt < retries:
        try:
            send_message(f"Rolex bhai attempt {attempt+1}… thoda intazaar karo, approx {min(2**attempt,10)} sec")
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code != 200:
                send_message(f"❌ Rolex bhai request failed: {r.status_code}")
                attempt += 1
                time.sleep(min(2**attempt,10))
                continue

            # JSON detection
            content_type = r.headers.get("Content-Type", "")
            if "application/json" in content_type:
                send_message("Rolex bhai 📦 JSON file mila")
                return r.json(), "json"
            else:
                # Try parsing JSON anyway if content-type wrong
                try:
                    return r.json(), "json"
                except:
                    pass

            # HTML parsing
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.title.string.strip() if soup.title else "No Title"
            send_message("Rolex bhai 📄 HTML file mil gaya")

            if mode == "telegram":
                authors, quotes = guess_classes(soup)
            else:
                authors = soup.find_all(
                    "small",
                    class_=lambda x: x and (author_class in x if author_class else True),
                )
                quotes = soup.find_all(
                    "span",
                    class_=lambda x: x and (quote_class in x if quote_class else True),
                )

            html_data = []
            for i in range(min(len(authors), len(quotes))):
                a = authors[i]
                q = quotes[i]
                html_data.append({
                    "author": a.text.strip() if a else None,
                    "quote": q.text.strip() if q else None,
                    "url": url,
                    "title": title
                })

            return html_data, "html"

        except Exception as e:
            logging.warning(f"Fetch attempt {attempt+1} failed: {e}")
            attempt += 1
            time.sleep(min(2**attempt,10))

    send_message(f"❌ Rolex bhai All {retries} attempts failed for {url}")
    return None, None

# -----------------------
# SAVE WITH ESTIMATED MSG
# -----------------------
def save(data, dtype):
    global data_store
    if not data:
        send_message("⚠️ Rolex bhai save skipped: data empty")
        return

    send_message("Rolex bhai 📦 Data process ho raha hai… lagbhag 2–5 sec lag sakta hai")

    if isinstance(data, list):
        data_store.extend(data)
    else:
        data_store.append(data)

    # JSON save
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(data_store, f, indent=2, ensure_ascii=False)
    send_message("Rolex bhai JSON file save ho gaya → output.json")

    # CSV + duplicate removal
    df = pd.DataFrame(data_store)
    df.drop_duplicates(inplace=True)
    df.to_csv("output.csv", index=False, encoding="utf-8-sig")
    send_message("Rolex bhai CSV save ho gaya → output.csv")
    send_message("Rolex bhai Panda se duplicates hata diye")

    send_message(f"✅ Rolex bhai {dtype.upper()} process complete")

# -----------------------
# PROCESS SINGLE URL
# -----------------------
def process_url(url, mode="manual"):
    url = fix_url(url)
    if not url or url in processed_urls:
        send_message(f"⚠️ Rolex bhai URL already processed or empty: {url}")
        return

    send_message(f"Rolex bhai 🔗 URL sahi hai, process ho raha hai… lagbhag 5–10 sec lag sakta hai: {url}")

    author_class = None
    quote_class = None
    if mode != "telegram":
        author_class = input("Author class (optional, press enter to skip): ").strip() or None
        quote_class = input("Quote class (optional, press enter to skip): ").strip() or None

    data, dtype = fetch(url, mode=mode, author_class=author_class, quote_class=quote_class)
    if data:
        save(data, dtype)
    else:
        send_message("❌ Rolex bhai data nahi mila")

    processed_urls.add(url)
    # Save processed URL persistently
    with open(PROCESSED_FILE,"w") as f:
        for u in processed_urls:
            f.write(u+"\n")

    send_message("🔒 Rolex bhai task complete, next input ka wait…")

# -----------------------
# PROCESS request.txt
# -----------------------
def process_txt():
    if not os.path.exists(REQUEST_FILE):
        send_message(f"❌ Rolex bhai {REQUEST_FILE} nahi mila")
        return
    with open(REQUEST_FILE, encoding="utf-8") as f:
        urls = [u.strip() for u in f if u.strip()]
    total = len(urls)
    for idx,u in enumerate(urls,1):
        send_message(f"Rolex bhai URL {idx}/{total} processing")
        process_url(u, mode="manual")

# -----------------------
# TELEGRAM MODE
# -----------------------
def telegram_mode():
    send_message("📡 Rolex bhai Telegram mode ON")
    while True:
        msg = get_updates()
        if msg:
            if msg.lower() in ["exit", "stop"]:
                send_message("❌ Rolex bhai Telegram mode OFF")
                break
            if "." in msg:
                process_url(msg, mode="telegram")
        time.sleep(2)

# -----------------------
# MAIN
# -----------------------
def main():
    welcome()
    send_message("🚀 Rolex bhai System ready")
    while True:
        menu()
        ch = input("Enter: ").strip().lower()
        if ch in ["exit", "q"]:
            send_message("👋 Rolex bhai System band")
            break
        elif ch == "1":
            process_txt()
        elif ch == "2":
            url = input("URL daalo: ")
            process_url(url, mode="manual")
        elif ch == "3":
            telegram_mode()
        else:
            print("⚠️ Invalid choice")

# -----------------------
# RUN
# -----------------------
if __name__ == "__main__":
    main()
