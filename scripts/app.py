import os
import sys
import duckdb
import streamlit as st

# Add both root and scripts directory to sys.path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "scripts"))

try:
    from live_scraper import scrape_and_store
except ModuleNotFoundError:
    from scripts.live_scraper import scrape_and_store

st.set_page_config(page_title="E-Commerce Live Pipeline Dashboard", layout="wide")
st.title("🛒 E-Commerce Real-Time Data Pipeline")

PROJECT_ROOT = os.getcwd()
DB_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, "data", "warehouse", "ecommerce.duckdb"))

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

if not os.path.exists(DB_PATH):
    st.info("Initializing DuckDB warehouse...")
    scrape_and_store()

st.subheader("⚡ Pipeline Controls")
if st.button("🔄 Trigger Live Web Scraper"):
    with st.spinner("Scraping live marketplace..."):
        scrape_and_store()
    st.success("Data updated successfully!")
    st.rerun()

st.divider()

con = duckdb.connect(DB_PATH, read_only=True)

total_items = con.execute("SELECT COUNT(*) FROM scraped_live_products").fetchone()[0] or 0
avg_price = con.execute("SELECT ROUND(AVG(price_gbp), 2) FROM scraped_live_products").fetchone()[0] or 0.0
in_stock = con.execute("SELECT COUNT(*) FROM scraped_live_products WHERE availability LIKE '%In stock%'").fetchone()[0] or 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Items Scraped", f"{total_items:,}")
col2.metric("Average Price", f"£{avg_price:,.2f}")
col3.metric("Items In Stock", f"{in_stock:,}")

st.divider()

st.subheader("📦 Live Catalog Warehouse")
df = con.execute("""
    SELECT 
        title AS "Product Title", 
        price_gbp AS "Price (£)", 
        availability AS "Availability", 
        scraped_at AS "Scraped At"
    FROM scraped_live_products
    ORDER BY scraped_at DESC
""").df()

st.dataframe(df, use_container_width=True)
con.close()
