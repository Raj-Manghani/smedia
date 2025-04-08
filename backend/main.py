from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncpg
import requests
from bs4 import BeautifulSoup
import re # For cleaning scraped data

app = FastAPI(title="Smedia Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://smedia_user:smedia_pass@postgres:5432/smedia_db",
)
db_pool = None


@app.on_event("startup")
async def startup():
    global db_pool
    db_pool = await asyncpg.create_pool(dsn=DB_URL, min_size=1, max_size=5)
    print("Database connection pool created")


@app.on_event("shutdown")
async def shutdown():
    await db_pool.close()
    print("Database connection pool closed")


@app.get("/")
async def root():
    return {"message": "Welcome to the Smedia Backend API"}


@app.get("/health")
async def health():
    return {"status": "ok"}


# --- Helper function for scraping (will be expanded) ---
def scrape_yahoo_finance(ticker: str):
    """
    Scrapes key statistics for a given ticker from Yahoo Finance.
    Returns a dictionary with stats or None if scraping fails.
    """
    stats = {}
    url = f"https://finance.yahoo.com/quote/{ticker}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Find elements containing the stats ---
        # Note: These selectors are based on Yahoo Finance structure as of late 2024/early 2025
        # They are fragile and might break if Yahoo changes its layout.

        # Market Cap
        market_cap_el = soup.find('td', {'data-test': 'MARKET_CAP-value'})
        if market_cap_el:
            stats['market_cap'] = market_cap_el.text

        # P/E Ratio (TTM)
        pe_ratio_el = soup.find('td', {'data-test': 'PE_RATIO-value'})
        if pe_ratio_el:
            stats['pe_ratio_ttm'] = pe_ratio_el.text

        # Volume
        volume_el = soup.find('td', {'data-test': 'TD_VOLUME-value'})
        if volume_el:
             # Remove commas for easier parsing later
            stats['volume'] = volume_el.text.replace(',', '')

        # Previous Close
        prev_close_el = soup.find('td', {'data-test': 'PREV_CLOSE-value'})
        if prev_close_el:
            stats['prev_close'] = prev_close_el.text

        # Open
        open_el = soup.find('td', {'data-test': 'OPEN-value'})
        if open_el:
            stats['open'] = open_el.text

        # Day's Range
        days_range_el = soup.find('td', {'data-test': 'DAYS_RANGE-value'})
        if days_range_el:
            stats['days_range'] = days_range_el.text

        # 52 Week Range
        fifty_two_week_range_el = soup.find('td', {'data-test': 'FIFTY_TWO_WK_RANGE-value'})
        if fifty_two_week_range_el:
            stats['fifty_two_week_range'] = fifty_two_week_range_el.text

        # --- Add more stats as needed ---

        # Basic validation: return None if no stats were found
        return stats if stats else None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Yahoo Finance page for {ticker}: {e}")
        return None
    except Exception as e:
        print(f"Error parsing Yahoo Finance page for {ticker}: {e}")
        return None


@app.get("/stock/{ticker}/stats")
async def get_stock_stats(ticker: str):
    """
    API endpoint to get key statistics for a stock ticker by scraping Yahoo Finance.
    """
    # Basic ticker validation (e.g., uppercase letters/numbers, length)
    if not re.match(r"^[A-Z0-9.-]{1,10}$", ticker):
         raise HTTPException(status_code=400, detail="Invalid ticker format")

    print(f"Attempting to scrape stats for ticker: {ticker}")
    stats = scrape_yahoo_finance(ticker)

    if stats is None:
        raise HTTPException(status_code=404, detail=f"Could not find or scrape stats for ticker: {ticker}")

    return JSONResponse(content=stats)


@app.get("/sentiment-feed")
async def sentiment_feed():
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, subreddit, author, title, selftext, created_utc, url,
                   tickers, sentiment, strength, keywords, permalink
            FROM posts
            ORDER BY created_utc DESC
            LIMIT 50
            """
        )
        posts = []
        for row in rows:
            posts.append(
                {
                    "id": row["id"],
                    "subreddit": row["subreddit"],
                    "author": row["author"],
                    "title": row["title"],
                    "selftext": row["selftext"],
                    "created_utc": row["created_utc"].isoformat()
                    if row["created_utc"]
                    else None,
                    "url": row["url"],
                    "tickers": row["tickers"],
                    "sentiment": row["sentiment"],
                    "strength": row["strength"],
                    "keywords": row["keywords"],
                    "permalink": row["permalink"],
                }
            )
        return JSONResponse(content=posts)
