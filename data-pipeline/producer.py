import os
import time
import json
import re
from kafka import KafkaProducer
import praw

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC = "raw_posts"

SUBREDDITS = ["wallstreetbets", "stocks", "investing", "pennystocks", "options"]

TICKER_PATTERN = re.compile(r'\b[A-Z]{1,5}\b')

def extract_tickers(text):
    return list(set(TICKER_PATTERN.findall(text)))

def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
    )

    print(f"Streaming subreddits: {SUBREDDITS}")

    while True:
        try:
            for subreddit_name in SUBREDDITS:
                subreddit = reddit.subreddit(subreddit_name)
                for post in subreddit.new(limit=20):
                    data = {
                        "id": post.id,
                        "subreddit": subreddit_name,
                        "title": post.title,
                        "selftext": post.selftext,
                        "created_utc": post.created_utc,
                        "url": post.url,
                        "author": str(post.author),
                        "tickers": extract_tickers(post.title + " " + post.selftext),
                        "permalink": f"https://reddit.com{post.permalink}"
                    }
                    producer.send(TOPIC, data)
                    print(f"Sent post {post.id} from r/{subreddit_name} with tickers {data['tickers']}")
            time.sleep(30)
        except Exception as e:
            print(f"Error fetching posts: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
