import time
import os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent


def get_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"


def get_selenium_options():
    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-insecure-localhost')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument(f'user-agent={get_user_agent()}')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('window-size=1920,1080')
    return options


def remove_webdriver_flag(driver):
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })


def scroll_down(driver, scroll_pause=2, max_scrolls=3):
    for i in range(max_scrolls):
        print(f"🔽 Scrolling ({i+1}/{max_scrolls})...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)


def is_heavy_javascript(content):
    soup = BeautifulSoup(content, 'html.parser')
    total_tags = len(soup.find_all())
    script_tags = len(soup.find_all('script'))
    ratio = script_tags / total_tags if total_tags > 0 else 0
    print(f"📊 Script tag ratio: {ratio:.2f}")
    return ratio > 0.3


def extract_article_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for link in soup.select("article a"):
        href = link.get("href")
        if href and href.startswith("/"):
            links.append("https://www.amazon.com" + href)
    return list(set(links))


def save_links_to_excel(links, page_title, filename):
    try:
        df = pd.DataFrame(links, columns=["URL"])
        df.insert(0, "Page Title", page_title)
        df.to_excel(filename, index=False)
        print(f"✅ Saved {len(links)} links to Excel file: '{filename}'")
    except Exception as e:
        print("❌ Error while saving Excel file:", str(e))


def selenium_scrape_with_retry(url, max_retries=3):
    options = get_selenium_options()
    for attempt in range(1, max_retries + 1):
        print(f"🔁 Attempt {attempt} to open: {url}")
        driver = webdriver.Chrome(service=ChromeService(), options=options)
        remove_webdriver_flag(driver)
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.title_contains("Amazon"))
            page_title = driver.title
            print(f"📄 Page title: {page_title}")

            scroll_down(driver)
            time.sleep(3)
            content = driver.page_source

            if is_heavy_javascript(content):
                print("⚠️ This page is heavy in JavaScript.")
            else:
                print("✅ This page is light on JavaScript.")

            links = extract_article_links(content)
            print(f"🔗 Found {len(links)} article links.")

            for link in links[:5]:
                print(" -", link)

            save_path = r"C:/Users/omar/OneDrive/Desktop/IR PROJECT/amazon.xlsx"
            save_links_to_excel(links, page_title, filename=save_path)

            driver.quit()
            return
        except Exception as e:
            print(f"❌ Error during attempt {attempt}: {e}")
            driver.quit()
            if attempt < max_retries:
                print("🔄 Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("🛑 Max retries reached. Exiting.")


if __name__ == "__main__":
    url = "https://www.amazon.com"
    selenium_scrape_with_retry(url)
