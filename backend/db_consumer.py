import asyncio
import json
import os
import asyncpg
from kafka import KafkaConsumer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://smedia_user:smedia_pass@postgres:5432/smedia_db",
)


async def insert_post(conn, post):
    try:
        await conn.execute(
            """
            INSERT INTO posts (
                id, subreddit, author, title, selftext, created_utc,
                url, tickers, sentiment, strength, keywords, permalink
            )
            VALUES (
                $1, $2, $3, $4, $5, $6,
                $7, $8, $9, $10, $11, $12
            )
            ON CONFLICT DO NOTHING
            """,
            post.get("id"),
            post.get("subreddit"),
            post.get("author"),
            post.get("title"),
            post.get("selftext"),
            post.get("created_utc"),
            post.get("url"),
            post.get("tickers"),
            post.get("sentiment"),
            post.get("strength"),
            post.get("keywords"),
            post.get("permalink"),
        )
    except Exception as e:
        print(f"DB insert error: {e}")


async def consume_and_store():
    conn = await asyncpg.connect(DB_URL)
    consumer = KafkaConsumer(
        "enriched_posts",
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="db-consumer-group",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    print("DB consumer started, waiting for messages...")
    try:
        for message in consumer:
            post = message.value
            # Convert epoch to datetime object
            if isinstance(post.get("created_utc"), (int, float)):
                import datetime
                post["created_utc"] = datetime.datetime.utcfromtimestamp(
                    post["created_utc"]
                )
            await insert_post(conn, post)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(consume_and_store())
