import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from crawl import CrawlabilityChecker
from ContentExtractor import AmazonContentExtractor
import os
import graphviz
from graphviz import Digraph
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile


# -------- Dummy Implementations for Testing --------
class CrawlabilityChecker:
    def can_crawl(self, url):
        # Dummy logic: disallow signin and wishlist URLs
        disallowed_keywords = ['signin', 'wishlist']
        return not any(word in url for word in disallowed_keywords)

class AmazonContentExtractor:
    def __init__(self, max_pages=1):
        self.max_pages = max_pages

    def crawl(self):
        # Return dummy product data as list of dicts
        return [
            {'product': 'Vacuum Cleaner', 'category': 'Home Essentials', 'price': 99.99},
            {'product': 'Dish Soap', 'category': 'Home Essentials', 'price': 5.49},
            {'product': 'LED Bulb', 'category': 'Home Essentials', 'price': 2.99},
            {'product': 'Smartphone Case', 'category': 'Electronics', 'price': 15.99},
            {'product': 'Hand Towel', 'category': 'Home Essentials', 'price': 7.99},
            {'product': 'Blender', 'category': 'Home Essentials', 'price': 45.00},
            {'product': 'Scented Candle', 'category': 'Home Essentials', 'price': 12.50},
            {'product': 'Coffee Maker', 'category': 'Home Essentials', 'price': 88.00},
        ]

def save_to_csv(products, path):
    df = pd.DataFrame(products)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)





# ---------- PAGE SETUP ----------
st.set_page_config(page_title="Crawling Tool Dashboard", layout="wide")

st.title(" Crawlability & Content Extraction Dashboard")
st.markdown("This dashboard visualizes crawlability scores, top extracted data, and scraping recommendations.")

# ---------- SECTION 1: CRAWLABILITY ----------
st.header("1.  Crawlability Score")

checker = CrawlabilityChecker()
urls = [
    'https://www.amazon.com/',
    'https://www.amazon.com/s?k=smartphones',
    'https://www.amazon.com/dp/B09G3HRMVP',
    'https://www.amazon.com/ap/signin',
    'https://www.amazon.com/gp/wishlist',
]

results = [{"URL": url, "Allowed": checker.can_crawl(url)} for url in urls]
df_crawl = pd.DataFrame(results)
st.dataframe(df_crawl)

# Score Calculation
allowed_count = df_crawl["Allowed"].sum()
total_count = len(df_crawl)
crawl_score = (allowed_count / total_count) * 100

st.metric(" Crawlability Score", f"{crawl_score:.1f}%")

# ---------- SECTION 2: TOP EXTRACTED PRODUCTS ----------
st.header("2.  Top Extracted Products (Home Essentials)")

# Check if CSV already exists
csv_path = "data/home_essentials_products.csv"
if not os.path.exists(csv_path):
    scraper = AmazonContentExtractor(max_pages=1)
    products = scraper.crawl()
    from ContentExtractor import save_to_csv
    save_to_csv(products, csv_path)

# Load data
df_products = pd.read_csv(csv_path)
st.dataframe(df_products.head(10))

# Visualization
st.subheader("Top Categories (Count)")
fig, ax = plt.subplots()
df_products['category'].value_counts().plot(kind='bar', ax=ax)
st.pyplot(fig)

# ---------- SECTION 3: RECOMMENDATIONS ----------
st.header("3.  Recommendations for Crawl & Extraction")

st.markdown("""
-  Use **Selenium** with dynamic scrolling and JavaScript rendering for product-heavy pages.
-  Include **random user-agent** headers and wait times to prevent IP blocks.
-  Avoid crawling login, cart, and review submission pages — typically disallowed.
-  Respect `robots.txt` rules (use `urllib.robotparser`).
-  Save extracted links to **CSV** for easy reprocessing.
-  Use retry logic to handle network errors or rendering issues.
""")

# ---------- SECTION 4: VISUAL SITEMAP ----------
st.header("4. 🗺️ Visual Sitemap of Crawling & Extraction Flow")

G = nx.DiGraph()

# Add nodes
nodes = {
    "A": "Amazon.com (Homepage)",
    "B": "Search Pages\n(e.g., ?k=smartphones)",
    "C": "Product Pages\n(e.g., /dp/B09G3HRMVP)",
    "D": "Wishlist Pages\n(e.g., /gp/wishlist)",
    "E": "Blocked Pages\n(Sign-in, Cart, Reviews)",
    "F": "Extracted Data",
    "G": "CSV Output",
    "H": "Dashboard Display"
}

for node_id, label in nodes.items():
    G.add_node(node_id, label=label)

# Add edges with labels
edges = [
    ("A", "B", "crawl"),
    ("B", "C", "follow links"),
    ("A", "D", "crawl"),
    ("A", "E", "blocked by robots.txt"),
    ("C", "F", "extract"),
    ("F", "G", "save"),
    ("G", "H", "load into dashboard"),
]

for src, dst, label in edges:
    G.add_edge(src, dst, label=label)

# Positioning nodes in a layout
pos = nx.spring_layout(G, seed=42)

# Draw graph with labels and edge labels
fig, ax = plt.subplots(figsize=(10, 6))
nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=2000, ax=ax)
nx.draw_networkx_labels(G, pos, labels=nodes, font_size=9, ax=ax)

nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20, edge_color='gray', ax=ax)
edge_labels = {(src, dst): lbl for src, dst, lbl in edges}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=8, ax=ax)

ax.axis('off')
st.pyplot(fig)