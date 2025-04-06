import requests

def test_sentiment_feed():
    try:
        resp = requests.get("http://localhost:8000/sentiment-feed", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        assert isinstance(data, list), "Response is not a list"
        for post in data:
            assert "sentiment" in post, "Missing 'sentiment' in post"
            assert "strength" in post, "Missing 'strength' in post"
            assert "keywords" in post, "Missing 'keywords' in post"
        print(f"Test passed: received {len(data)} enriched posts with sentiment data.")
    except Exception as e:
        print(f"Sentiment feed test failed: {e}")
        exit(1)

if __name__ == "__main__":
    test_sentiment_feed()
