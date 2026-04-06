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

def main():
    results = []
    while True:
        url = input("Enter URL (or 'exit' to quit): ").strip()
        if url.lower() == "exit":
            break
        if not url:
            continue

        results.append(fetch_url(url))

        # Save JSON
        with open("output.json", "w") as jf:
            json.dump(results, jf, indent=2)

        # Save CSV
        df = pd.DataFrame(results)
        df.to_csv("output.csv", index=False)
        print(f"Processed {url} ✅\nCSV + JSON updated")

if __name__ == "__main__":
    main()
