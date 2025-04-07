import os
import json
import pytest
from kafka import KafkaConsumer


@pytest.mark.skipif(
    os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true",
    reason="Skip integration test in CI environment"
)
def test_reddit_ingestion():
    consumer = KafkaConsumer(
        'raw_posts',
        bootstrap_servers=os.getenv("KAFKA_BROKER", "localhost:9092"),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='test-consumer-group',
        consumer_timeout_ms=10000,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    messages = []
    for message in consumer:
        messages.append(message.value)
        if len(messages) >= 5:
            break

    assert len(messages) > 0, "No messages received from raw_posts topic"

    required_fields = {
        "id", "subreddit", "title", "selftext", "created_utc",
        "url", "author", "tickers", "permalink"
    }

    for msg in messages:
        missing = required_fields - msg.keys()
        assert not missing, f"Missing fields in message: {missing}"

    print(
        f"Test passed: received {len(messages)} valid messages "
        f"from raw_posts topic."
    )


if __name__ == "__main__":
    test_reddit_ingestion()
