import urllib.robotparser
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse

class CrawlabilityChecker:
    def __init__(self, robots_url='https://www.amazon.com/robots.txt'):
        self.robots_url = robots_url
        self.parser = urllib.robotparser.RobotFileParser()
        self._load_robots_txt()

    def _load_robots_txt(self):
        try:
            self.parser.set_url(self.robots_url)
            self.parser.read()
            print(f"✅ Loaded robots.txt from {self.robots_url}")
        except (URLError, HTTPError) as e:
            print(f"❌ Failed to load robots.txt: {e}")
            self.parser = None

    def can_crawl(self, url, user_agent='*'):
        if self.parser is None:
            print("⚠️ robots.txt parser not initialized.")
            return False

        path = urlparse(url).path  # extract just the path part
        is_allowed = self.parser.can_fetch(user_agent, path)
        reason = "ALLOWED ✅" if is_allowed else "BLOCKED ❌"
        print(f"[{user_agent}] {reason} -> {path}")
        return is_allowed

# === USAGE ===
checker = CrawlabilityChecker()
urls_to_check = [
    # === Homepage & Category Pages ===
    'https://www.amazon.com/',
    'https://www.amazon.com/s?k=smartphones',
    'https://www.amazon.com/gp/bestsellers',
    'https://www.amazon.com/gp/new-releases',
    
    # === Product Pages ===
    'https://www.amazon.com/dp/B09G3HRMVP',
    'https://www.amazon.com/dp/B00005N5PF',

    # === Wishlist & Lists ===
    'https://www.amazon.com/wishlist/universal',
    'https://www.amazon.com/wishlist',
    'https://www.amazon.com/gp/wishlist',

    # === Reviews ===
    'https://www.amazon.com/product-reviews/B09G3HRMVP',
    'https://www.amazon.com/gp/customer-reviews/write-a-review.html',

    # === Sign-in & Cart ===
    'https://www.amazon.com/gp/cart',
    'https://www.amazon.com/ap/signin',

    # === Media & Video ===
    'https://www.amazon.com/gp/video/library',
    'https://www.amazon.com/gp/video/search',

    # === Help & Contact ===
    'https://www.amazon.com/gp/help/customer/display.html',
    'https://www.amazon.com/hz/contact-us',

    # === Deals & Offers ===
    'https://www.amazon.com/gp/goldbox',
    'https://www.amazon.com/s?k=deals',

    # === Sitemap (test if available) ===
    'https://www.amazon.com/sitemap.xml',

    # === Disallowed Patterns ===
    'https://www.amazon.com/gp/registry/wishlist/XYZ/reserve',
    'https://www.amazon.com/review/common/du',
    'https://www.amazon.com/exec/obidos/account-access-login',

    # === Allowed Exceptions ===
    'https://www.amazon.com/gp/wishlist/universal',
    'https://www.amazon.com/gp/wishlist/ipad-install'
]


for url in urls_to_check:
    checker.can_crawl(url)
