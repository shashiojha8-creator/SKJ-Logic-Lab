import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import logging
from functools import wraps

# Logger
logging.basicConfig(filename="scraper.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Decorator
def safe_run(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            return {"url": args[0], "title": "No Data / Error"}
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
    with open("urls.txt") as f:
        urls = [u.strip() for u in f.readlines() if u.strip()]

    results = [fetch_url(url) for url in urls]

    with open("output.json", "w") as jf:
        json.dump(results, jf, indent=2)

    df = pd.DataFrame(results)
    df.to_csv("output.csv", index=False)
    logging.info("JSON + CSV created successfully")
    print("Done ✅")

if __name__ == "__main__":
    main()
