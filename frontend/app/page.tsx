"use client";

import React, { useEffect, useState } from "react";

interface Post {
  id: string;
  title: string;
  subreddit: string;
  author: string;
  sentiment: string;
  strength: number;
  tickers: string[];
  keywords: string[];
  permalink: string;
}

export default function HomePage() {
  const [posts, setPosts] = useState<Post[]>([]);

  useEffect(() => {
    async function fetchData() {
      try {
        const resp = await fetch("http://localhost:8000/sentiment-feed");
        const data = await resp.json();
        setPosts(data);
      } catch (error) {
        console.error("Error fetching sentiment feed:", error);
      }
    }

    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-gray-900 text-white p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">Smedia Stock Sentiment Dashboard</h1>
        <nav>
          <a href="#" className="mx-2 hover:underline">Live Feed</a>
          <a href="#" className="mx-2 hover:underline">Tickers</a>
          <a href="#" className="mx-2 hover:underline">Settings</a>
        </nav>
      </header>

      <main className="flex flex-1">
        <aside className="w-64 bg-gray-100 p-4 border-r hidden md:block">
          <h2 className="font-semibold mb-4">Navigation</h2>
          <ul>
            <li className="mb-2"><a href="#" className="hover:underline">Live Feed</a></li>
            <li className="mb-2"><a href="#" className="hover:underline">Tickers</a></li>
            <li className="mb-2"><a href="#" className="hover:underline">Settings</a></li>
          </ul>
        </aside>

        <section className="flex-1 p-6 overflow-y-auto">
          <h2 className="text-2xl font-semibold mb-4">Live Sentiment Feed</h2>
          <div className="border rounded p-4 mb-6 max-h-[600px] overflow-y-auto">
            {posts.length === 0 ? (
              <p>Loading sentiment data...</p>
            ) : (
              posts.map((post) => (
                <div key={post.id} className="mb-4 border-b pb-2">
                  <div className="font-semibold">{post.title}</div>
                  <div className="text-sm text-gray-600">{post.subreddit} by {post.author}</div>
                  <div className="mt-1">Sentiment: <strong>{post.sentiment}</strong> (Strength: {post.strength})</div>
                  <div className="mt-1">Tickers: {post.tickers && post.tickers.join(", ")}</div>
                  <div className="mt-1">Keywords: {post.keywords && post.keywords.join(", ")}</div>
                  <a href={post.permalink} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">View on Reddit</a>
                </div>
              ))
            )}
          </div>

          <h2 className="text-2xl font-semibold mb-4">Top Tickers</h2>
          <div className="border rounded p-4 mb-6">
            <p>Most discussed tickers with sentiment breakdown will appear here.</p>
          </div>

          <h2 className="text-2xl font-semibold mb-4">Sentiment Heatmap</h2>
          <div className="border rounded p-4 mb-6">
            <p>Visual heatmap of sentiment by ticker will appear here.</p>
          </div>

          <h2 className="text-2xl font-semibold mb-4">Settings</h2>
          <div className="border rounded p-4">
            <p>Configure API keys, select LLM models, and other preferences here.</p>
          </div>
        </section>
      </main>

      <footer className="bg-gray-900 text-white p-4 text-center">
        &copy; 2025 Smedia Sentiment App
      </footer>
    </div>
  );
}
