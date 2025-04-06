from fastapi import FastAPI
from fastapi.responses import JSONResponse
import threading
import json
import os
from kafka import KafkaConsumer

app = FastAPI(title="Smedia Backend API")

enriched_posts_cache = []

def kafka_consumer_thread():
    broker = os.getenv("KAFKA_BROKER", "kafka:9092")
    consumer = KafkaConsumer(
        "enriched_posts",
        bootstrap_servers=broker,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='backend-feed-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    for message in consumer:
        enriched_posts_cache.append(message.value)
        # Keep only last 100 posts
        if len(enriched_posts_cache) > 100:
            enriched_posts_cache.pop(0)

threading.Thread(target=kafka_consumer_thread, daemon=True).start()

@app.get("/")
async def root():
    return {"message": "Welcome to the Smedia Backend API"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/sentiment-feed")
async def sentiment_feed():
    return JSONResponse(content=enriched_posts_cache[-50:])
