import os
import json
import time
from kafka import KafkaConsumer, KafkaProducer
import requests

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
INPUT_TOPIC = "raw_posts"
OUTPUT_TOPIC = "enriched_posts"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1",
)


def analyze_sentiment(text):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Smedia Sentiment App",
        "Content-Type": "application/json",
    }
    prompt = (
        "Classify the sentiment of the following Reddit post as Positive, "
        "Neutral, or Negative. Also provide a strength score (0-1) and key "
        "phrases that influenced your decision.\n\nPost:\n"
        f"{text}\n\nRespond in JSON with keys 'sentiment', 'strength', 'keywords'."
    )

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150,
        "temperature": 0.2,
    }

    try:
        resp = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=30,
        )
        resp.raise_for_status()
        response_text = (
            resp.json()["choices"][0]["message"]["content"]
        )
        result = json.loads(response_text)
        return result
    except Exception as e:
        print(f"LLM API error: {e}")
        return {"sentiment": "Unknown", "strength": 0, "keywords": []}


def main():
    consumer = KafkaConsumer(
        INPUT_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='nlp-service-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    )

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    )

    print("NLP service started, waiting for messages...")

    for message in consumer:
        post = message.value
        print(
            f"Received post {post.get('id')} from subreddit "
            f"{post.get('subreddit')}"
        )
        combined_text = post.get("title", "") + "\n" + post.get("selftext", "")
        print("Calling LLM for sentiment analysis...")
        sentiment_result = analyze_sentiment(combined_text)
        print(f"LLM response: {sentiment_result}")
        enriched_post = {**post, **sentiment_result}
        producer.send(OUTPUT_TOPIC, enriched_post)
        print(
            f"Published enriched post {post.get('id')} with sentiment "
            f"{sentiment_result.get('sentiment')}"
        )


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Error in NLP service: {e}")
            time.sleep(5)
