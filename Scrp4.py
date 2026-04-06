import os
import time
import threading
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import logging
from functools import wraps

# Logger
logging.basicConfig(filename="pro_scraper.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Decorator
def safe_run(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            return {"url": args[0] if args else "Unknown", "title": "No Data / Error"}
    return wrapper

@safe_run
def fetch_url(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            raise Exception("Request failed")
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "No Title"
        logging.info(f"Fetched {url}")
        return {"url": url, "title": title}
    except Exception as e:
        logging.warning(f"Fetching failed for {url}: {e}")
        return {"url": url, "title": "No Data / Error"}

@safe_run
def process_urls(file_path="urls.txt"):
    with open(file_path) as f:
        urls = [u.strip() for u in f.readlines() if u.strip()]
    results = [fetch_url(url) for url in urls]

    # Save JSON
    with open("output.json", "w") as jf:
        json.dump(results, jf, indent=2)

    # Save CSV + remove duplicates
    df = pd.DataFrame(results)
    df.drop_duplicates(inplace=True)
    df.to_csv("output.csv", index=False)
    logging.info(f"Processed {len(df)} URLs → output.csv + output.json")
    print(f"Processed {len(df)} URLs ✅")

def watch_file(file_path="urls.txt"):
    last_modified = None
    print(f"Monitoring {file_path} for changes...")
    while True:
        try:
            mtime = os.path.getmtime(file_path)
            if last_modified is None or mtime != last_modified:
                last_modified = mtime
                print("Change detected → Processing")
                t = threading.Thread(target=process_urls)
                t.start()
            time.sleep(2)
        except KeyboardInterrupt:
            print("Stopped by user.")
            break
        except FileNotFoundError:
            time.sleep(2)

if __name__ == "__main__":
    watch_file()
