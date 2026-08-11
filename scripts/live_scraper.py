import os
import re
import duckdb
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_and_store():
    url = "http://books.toscrape.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data, status code: {response.status_code}")
        
    soup = BeautifulSoup(response.text, "html.parser")
    products = soup.find_all("article", class_="product_pod")
    
    scraped_data = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for product in products:
        title = product.h3.a["title"]
        price_raw = product.find("p", class_="price_color").text
        price = float(re.sub(r"[^\d.]", "", price_raw))
        availability = product.find("p", class_="instock availability").text.strip()
        
        scraped_data.append((title, price, availability, timestamp))
        
    PROJECT_ROOT = os.getcwd()
    db_path = os.path.abspath(os.path.join(PROJECT_ROOT, "data", "warehouse", "ecommerce.duckdb"))
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    con = duckdb.connect(db_path)
    con.execute("""
        CREATE TABLE IF NOT EXISTS scraped_live_products (
            title VARCHAR,
            price_gbp DOUBLE,
            availability VARCHAR,
            scraped_at TIMESTAMP
        )
    """)
    
    for row in scraped_data:
        con.execute("""
            INSERT INTO scraped_live_products (title, price_gbp, availability, scraped_at)
            VALUES (?, ?, ?, ?)
        """, row)
        
    con.close()
    print("Scraping and DuckDB update completed successfully.")

if __name__ == "__main__":
    scrape_and_store()
