import os
import time
import threading
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

def fetch_url(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            raise Exception("Request failed")
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "No Title"
        return {"url": url, "title": title}
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {"url": url, "title": "No Data / Error"}

def process_urls(file_path="urls.txt"):
    try:
        with open(file_path) as f:
            urls = [u.strip() for u in f.readlines() if u.strip()]
        results = [fetch_url(url) for url in urls]

        # Save JSON + CSV
        with open("output.json", "w") as jf:
            json.dump(results, jf, indent=2)

        df = pd.DataFrame(results)
        df.to_csv("output.csv", index=False)
        print(f"Processed {len(results)} URLs ✅")
    except Exception as e:
        print("Error in process_urls:", e)

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
