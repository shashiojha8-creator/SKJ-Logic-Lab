import requests
from bs4 import BeautifulSoup
import csv
import time
import random

def scrape_quotes_csv(filename="quotes.csv"):
    url = "http://quotes.toscrape.com/page/1/"
    base_url = "http://quotes.toscrape.com"

    data = []

    while url:
        try:
            # Human-like headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }

            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            quotes = soup.find_all("span", class_="text")
            authors = soup.find_all("small", class_="author")

            for author, quote in zip(authors, quotes):
                data.append([author.text.strip(), quote.text.strip()])

            # Next button logic
            next_btn = soup.find("li", class_="next")
            if next_btn:
                next_link = next_btn.find("a")["href"]
                url = base_url + next_link
            else:
                url = None

            # Random delay to mimic human browsing
            time.sleep(random.randint(1, 3))

        except Exception as e:
            print("Error occurred:", e)
            break

    # Save to CSV
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Author", "Quote"])
        writer.writerows(data)

    print(f"{filename} saved successfully ✅")

# 🔥 Call the function
scrape_quotes_csv()
