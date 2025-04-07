from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncpg

app = FastAPI(title="Smedia Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_URL = os.getenv("DATABASE_URL", "postgresql://smedia_user:smedia_pass@postgres:5432/smedia_db")
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

@app.get("/sentiment-feed")
async def sentiment_feed():
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, subreddit, author, title, selftext, created_utc, url, tickers, sentiment, strength, keywords, permalink
            FROM posts
            ORDER BY created_utc DESC
            LIMIT 50
            """
        )
        posts = []
        for row in rows:
            posts.append({
                "id": row["id"],
                "subreddit": row["subreddit"],
                "author": row["author"],
                "title": row["title"],
                "selftext": row["selftext"],
                "created_utc": row["created_utc"].isoformat() if row["created_utc"] else None,
                "url": row["url"],
                "tickers": row["tickers"],
                "sentiment": row["sentiment"],
                "strength": row["strength"],
                "keywords": row["keywords"],
                "permalink": row["permalink"],
            })
        return JSONResponse(content=posts)
