import os
import requests
import praw

def test_reddit():
    print("Testing Reddit API...")
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
        )
        me = reddit.user.me()
        print(f"Reddit auth successful. Logged in as: {me}")
    except Exception as e:
        print(f"Reddit API test failed: {e}")

def test_openrouter():
    print("Testing OpenRouter API...")
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Smedia Sentiment App"
        }
        resp = requests.get(f"{os.getenv('OPENROUTER_BASE_URL')}/models", headers=headers)
        if resp.status_code == 200:
            print("OpenRouter API key is valid.")
        else:
            print(f"OpenRouter API test failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"OpenRouter API test failed: {e}")

def test_polygon():
    print("Testing Polygon.io API...")
    try:
        url = f"{os.getenv('STOCK_API_BASE_URL')}/v2/aggs/ticker/AAPL/prev?adjusted=true&apiKey={os.getenv('STOCK_API_KEY')}"
        resp = requests.get(url)
        if resp.status_code == 200:
            print("Polygon.io API key is valid.")
        else:
            print(f"Polygon.io API test failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Polygon.io API test failed: {e}")

if __name__ == "__main__":
    test_reddit()
    test_openrouter()
    test_polygon()
