import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import random
import pandas as pd
import os

class AmazonContentExtractor:
    def __init__(self, base_url="https://www.amazon.com/s?i=home", keyword="home essentials", max_pages=3):
        self.base_url = base_url
        self.keyword = keyword
        self.max_pages = max_pages
        self.headers = {
            "User-Agent": UserAgent().random,
            "Accept-Language": "en-US,en;q=0.9"
        }

    def crawl(self):
        all_products = []
        for page in range(1, self.max_pages + 1):
            url = f"{self.base_url}&page={page}"
            print(f"📄 Crawling page {page}: {url}")
            response = requests.get(url, headers=self.headers)

            if response.status_code != 200:
                print(f"❌ Failed to fetch page {page}")
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            products = self.extract_products(soup)
            all_products.extend(products)

            delay = random.uniform(2, 5)
            print(f"⏳ Sleeping for {delay:.2f} seconds")
            time.sleep(delay)

        return all_products

    def extract_products(self, soup):
        items = soup.select("div.s-result-item")
        results = []

        for item in items:
            try:
                name = item.select_one("h2 span") and item.select_one("h2 span").text.strip()
                price_whole = item.select_one(".a-price .a-price-whole")
                price_fraction = item.select_one(".a-price .a-price-fraction")
                price = None
                if price_whole and price_fraction:
                    price = f"${price_whole.text.strip()}.{price_fraction.text.strip()}"

                rating = item.select_one(".a-icon-alt")
                customer_ratings = rating.text.strip() if rating else None

                image = item.select_one("img.s-image")
                image_url = image["src"] if image else None

                if name:
                    results.append({
                        "name": name,
                        "price": price,
                        "customer_ratings": customer_ratings,
                        "category": self.keyword,
                        "image": image_url
                    })

            except Exception as e:
                print(f"⚠️ Skipped item due to error: {e}")
                continue

        return results

def save_to_csv(products, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df = pd.DataFrame(products)
    df.to_csv(filepath, index=False)
    print(f"✅ CSV saved to: {filepath}")



# Home essentials / kitchen appliances keywords
home_essentials_keywords = [
    "kitchen appliances",
    "cookware sets",
    "blenders",
    "coffee makers",
    "microwaves",
    "air fryers",
    "toasters",
    "dishwashers"
]

all_products = []

for keyword in home_essentials_keywords:
    print(f"\n🔍 Searching for: {keyword}")
    search_url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}"
    scraper = AmazonContentExtractor(base_url=search_url, keyword=keyword, max_pages=2)
    products = scraper.crawl()

    print(f"🧮 Found {len(products)} products for '{keyword}'")

    for i, product in enumerate(products[:5], 1):
        print(f"\n--- Product {i} ---")
        for key, value in product.items():
            print(f"{key}: {value}")

    all_products.extend(products)

# Save results
save_to_csv(all_products, "data/home_essentials_products.csv")
