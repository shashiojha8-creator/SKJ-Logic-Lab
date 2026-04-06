import os
import time
import requests
import pandas as pd
import json
import logging
from bs4 import BeautifulSoup

# -----------------------
# LOGGING
# -----------------------
logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -----------------------
# SOUND
# -----------------------
def sound():
    os.system("echo -e '\a'")

# -----------------------
# ROLEX STYLE MESSAGE
# -----------------------
def rolex(msg):
    full_msg = f"🔥 Rolex bhai: {msg}"
    print(full_msg)
    logging.info(full_msg)

# -----------------------
# DECORATOR
# -----------------------
def log_function(func):
    def wrapper(*args, **kwargs):
        logging.info(f"START: {func.__name__}")
        result = func(*args, **kwargs)
        logging.info(f"END: {func.__name__}")
        return result
    return wrapper

# -----------------------
# GLOBALS
# -----------------------
data_store = []
processed_urls = set()
HEADERS = {"User-Agent": "Mozilla/5.0"}
REQUEST_FILE = "request.txt"

# -----------------------
# FETCH URL
# -----------------------
@log_function
def fetch(url):
    rolex("server ko request bhej rahe hain 🌐")

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)

        if r.status_code != 200:
            rolex("request fail ho gaya ❌")
            return None, None

        if "application/json" in r.headers.get("Content-Type", ""):
            rolex("JSON mil gaya 📦")
            sound()
            return r.json(), "json"

        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string.strip() if soup.title else None

        if not title:
            return None, None

        rolex("HTML mil gaya 📄")
        sound()
        return {"url": url, "title": title}, "html"

    except Exception as e:
        logging.error(f"Fetch error: {e}")
        rolex("fetch error ❌")
        return None, None

# -----------------------
# SAVE DATA
# -----------------------
@log_function
def save(data, dtype):
    global data_store

    if not data:
        rolex("kuch valid data nahi mila ⚠️")
        return

    data_store.append(data)

    try:
        # JSON
        with open("output.json", "w") as f:
            json.dump(data_store, f, indent=2)

        # CSV
        df = pd.DataFrame(data_store)
        df.drop_duplicates(inplace=True)
        df.to_csv("output.csv", index=False)

        rolex("CSV me save kar diya 📊")
        rolex("JSON me bhi save ho gaya 💾")
        sound()

    except Exception as e:
        logging.error(f"Save error: {e}")
        rolex("save error ❌")

# -----------------------
# PROCESS SINGLE URL
# -----------------------
@log_function
def process_url(url):
    if not url.startswith("http"):
        url = "https://" + url

    if url in processed_urls:
        rolex("already processed ⚠️")
        return

    rolex(f"URL mila: {url} 🔗")
    rolex("processing start ⏳")

    data, dtype = fetch(url)

    if data:
        save(data, dtype)
        processed_urls.add(url)
        rolex("kaam complete 🎯")
    else:
        rolex("data nahi mila ❌")

# -----------------------
# PROCESS request.txt
# -----------------------
def process_txt():
    if not os.path.exists(REQUEST_FILE):
        rolex("request.txt nahi mila ❌")
        return

    with open(REQUEST_FILE) as f:
        urls = [u.strip() for u in f if u.strip()]

    for u in urls:
        process_url(u)

# -----------------------
# TELEGRAM MODE
# -----------------------
def telegram_mode():
    rolex("Telegram mode ON 📡 (simple demo)")

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    if not BOT_TOKEN or not CHAT_ID:
        rolex("BOT_TOKEN ya CHAT_ID missing ❌")
        return

    last_update_id = None

    while True:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        if last_update_id:
            url += f"?offset={last_update_id + 1}"

        try:
            res = requests.get(url, timeout=5).json()
            for upd in res.get("result", []):
                last_update_id = upd["update_id"]

                if "message" in upd:
                    msg = upd["message"].get("text", "")
                    if msg.lower() in ["exit", "stop"]:
                        rolex("Telegram mode OFF ❌")
                        return

                    if "." in msg:
                        process_url(msg)

        except Exception as e:
            logging.error(f"Telegram fetch error: {e}")

        time.sleep(2)

# -----------------------
# MAIN MENU
# -----------------------
def main():
    print("\n🔥 Rolex Scraper Ready 🔥")

    while True:
        print("\n📌 Kya karna hai:")
        print("1 → request.txt scrape")
        print("2 → manual URL")
        print("3 → Telegram mode")
        print("4 → Extra / future option")
        print("exit → band karo")

        ch = input("👉 Choice: ").strip().lower()

        if ch in ["exit", "q"]:
            rolex("system band 👋")
            break

        elif ch == "1":
            process_txt()

        elif ch == "2":
            url = input("👉 URL daalo: ")
            process_url(url)

        elif ch == "3":
            telegram_mode()

        elif ch == "4":
            rolex("Future / Extra feature placeholder 🚀")

        else:
            print("❌ invalid")

        time.sleep(1)

# -----------------------
# RUN
# -----------------------
if __name__ == "__main__":
    main()
