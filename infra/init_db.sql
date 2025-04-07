CREATE EXTENSION IF NOT EXISTS timescaledb;

DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
    id TEXT NOT NULL,
    subreddit TEXT NOT NULL,
    author TEXT,
    title TEXT,
    selftext TEXT,
    created_utc TIMESTAMPTZ NOT NULL,
    url TEXT,
    tickers TEXT[],
    sentiment TEXT,
    strength FLOAT,
    keywords TEXT[],
    permalink TEXT,
    inserted_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (id, created_utc)
);

SELECT create_hypertable('posts', 'created_utc', if_not_exists => TRUE);
