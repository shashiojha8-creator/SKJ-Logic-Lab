import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import logging
from functools import wraps

logging.basicConfig(filename="scraper.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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
    r = requests.get(url, timeout=5)
    if r.status_code != 200:
        raise Exception("Request failed")
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.title.string.strip() if soup.title else "No Title"
    logging.info(f"Fetched {url}")
    return {"url": url, "title": title}

def main():
    results = []
    while True:
        url = input("Enter URL (or 'exit' to quit): ").strip()
        if url.lower() == "exit":
            break
        if not url:
            continue

        results.append(fetch_url(url))

        with open("output.json", "w") as jf:
            json.dump(results, jf, indent=2)

        df = pd.DataFrame(results)
        df.to_csv("output.csv", index=False)
        logging.info(f"Processed {url} → CSV + JSON updated")
        print(f"Processed {url} ✅\nCSV + JSON updated")

if __name__ == "__main__":
    main()
