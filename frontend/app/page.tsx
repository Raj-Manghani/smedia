"use client";

import React, { useEffect, useState } from "react";
import PostCard from '../components/PostCard'; // Import the new component

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
  created_utc: string | null;
}

// Define structure for grouped posts
interface GroupedPosts {
  Positive: Post[];
  Neutral: Post[];
  Negative: Post[];
  Unknown: Post[];
}

// Helper function for sentiment styling
function getSentimentBgColor(sentiment: string): string {
  switch (sentiment) {
    case 'Positive': return 'bg-green-100 text-green-800';
    case 'Negative': return 'bg-red-100 text-red-800';
    case 'Neutral': return 'bg-yellow-100 text-yellow-800';
    default: return 'bg-gray-100 text-gray-800';
  }
}


export default function HomePage() {
  // State to hold grouped posts
  const [groupedPosts, setGroupedPosts] = useState<GroupedPosts>({
    Positive: [],
    Neutral: [],
    Negative: [],
    Unknown: [],
  });

  useEffect(() => {
    async function fetchData() {
       try {
        const resp = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/sentiment-feed`);
        const data: Post[] = await resp.json();

        // Group posts by sentiment
        const newGroupedPosts: GroupedPosts = { Positive: [], Neutral: [], Negative: [], Unknown: [] };
        data.forEach(post => {
          // Ensure tickers and keywords are arrays even if null/undefined from API
          post.tickers = post.tickers || [];
          post.keywords = post.keywords || [];

          switch (post.sentiment) {
            case 'Positive':
              newGroupedPosts.Positive.push(post);
              break;
            case 'Neutral':
              newGroupedPosts.Neutral.push(post);
              break;
            case 'Negative':
              newGroupedPosts.Negative.push(post);
              break;
            default:
              // Handle potential null/undefined sentiment or other values
              post.sentiment = post.sentiment || 'Unknown';
              newGroupedPosts.Unknown.push(post);
              break;
          }
        });

        // Sort posts within each group by date (newest first)
        Object.values(newGroupedPosts).forEach(group => {
           group.sort((a: Post, b: Post) => // Added Post type annotation
             (b.created_utc && a.created_utc)
               ? new Date(b.created_utc).getTime() - new Date(a.created_utc).getTime()
               : 0
           );
        });

        setGroupedPosts(newGroupedPosts); // Update state with grouped data
      } catch (error) {
        console.error("Error fetching and grouping sentiment feed:", error);
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
          <h2 className="text-2xl font-semibold mb-4">Live Sentiment Feed (Grouped by Sentiment)</h2>

          {/* Render posts grouped by sentiment */}
          {Object.entries(groupedPosts).map(([sentiment, postsInGroup]) => (
            // Only render the section if there are posts in this group
            postsInGroup.length > 0 && (
              <div key={sentiment} className="mb-8"> {/* Increased margin bottom */}
                {/* Sentiment Group Header */}
                <h3 className={`text-xl font-semibold mb-3 p-2 rounded ${getSentimentBgColor(sentiment)}`}>
                  {sentiment} Sentiment ({postsInGroup.length} posts)
                </h3>
                {/* Scrollable container for posts within the group */}
                <div className="border rounded p-4 max-h-[450px] overflow-y-auto space-y-4"> {/* Added space-y-4 */}
                  {postsInGroup.map((post: Post) => ( // Added Post type annotation
                    // Use the PostCard component
                    <PostCard key={post.id} post={post} />
                  ))}
                </div>
              </div>
            )
          ))}

           {/* Loading Indicator */}
           {Object.values(groupedPosts).every(group => group.length === 0) && (
             <p className="text-gray-500">Loading sentiment data or no posts found...</p>
           )}

          {/* Placeholder Sections */}
          <h2 className="text-2xl font-semibold mb-4 mt-8">Top Tickers</h2> {/* Added margin top */}
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
