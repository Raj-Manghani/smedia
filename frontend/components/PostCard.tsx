"use client";

import React, { useState, useCallback } from 'react'; // Added useCallback

// Re-using the Post interface definition
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

// Interface for stock stats data
interface StockStats {
  market_cap?: string;
  pe_ratio_ttm?: string;
  volume?: string;
  prev_close?: string;
  open?: string;
  days_range?: string;
  fifty_two_week_range?: string;
  // Add more stats as needed
}

// Interface for the state managing stats per ticker
interface TickerStatsState {
  [ticker: string]: {
    loading: boolean;
    error: string | null;
    data: StockStats | null;
  };
}

interface PostCardProps {
  post: Post;
}

const PostCard: React.FC<PostCardProps> = ({ post }) => {
  const [showKeywords, setShowKeywords] = useState(false);
  const [tickerStats, setTickerStats] = useState<TickerStatsState>({}); // Added state for ticker stats

  const toggleKeywords = () => {
    setShowKeywords(!showKeywords);
  };

  // Function to fetch stats for a specific ticker
  const fetchStockStats = useCallback(async (ticker: string) => {
    // Don't fetch if already loading or data exists
    if (tickerStats[ticker]?.loading || tickerStats[ticker]?.data) {
      // Simple toggle visibility: If data exists, set it to null to hide, otherwise fetch.
      // This allows clicking again to hide the stats.
      if (tickerStats[ticker]?.data) {
        setTickerStats(prev => ({ ...prev, [ticker]: { ...prev[ticker], data: null, error: null } }));
        return;
      }
      // If loading, do nothing
      if (tickerStats[ticker]?.loading) {
        return;
      }
    }

    setTickerStats(prev => ({
      ...prev,
      [ticker]: { loading: true, error: null, data: null }
    }));

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'; // Fallback URL
      const resp = await fetch(`${apiUrl}/stock/${ticker}/stats`);

      if (!resp.ok) {
        const errorData = await resp.json();
        throw new Error(errorData.detail || `Failed to fetch stats for ${ticker} (${resp.status})`);
      }

      const data: StockStats = await resp.json();
      setTickerStats(prev => ({
        ...prev,
        [ticker]: { loading: false, error: null, data: data }
      }));
    } catch (error: unknown) { // Explicitly type error as unknown
      console.error(`Error fetching stats for ${ticker}:`, error);
      // Type check before accessing message property
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch stats';
      setTickerStats(prev => ({
        ...prev,
        [ticker]: { loading: false, error: errorMessage, data: null } // Use checked errorMessage
      }));
    }
  }, [tickerStats]); // Dependency array includes tickerStats

  return (
    <div className="border-b pb-3 mb-4"> {/* Added margin bottom */}
      {/* Post Header: Title and Timestamp */}
      <div className="flex justify-between items-start mb-1"> {/* Use items-start */}
        <span className="font-semibold text-base mr-2">{post.title}</span> {/* Slightly larger title */}
        <span className="text-xs text-gray-500 whitespace-nowrap"> {/* Prevent wrapping */}
          {post.created_utc ? new Date(post.created_utc).toLocaleString() : 'No date'}
        </span>
      </div>
      {/* Subreddit and Author */}
      <div className="text-sm text-gray-600 mb-1">
        r/{post.subreddit} by u/{post.author || 'deleted'} {/* Handle deleted author */}
      </div>
      {/* Sentiment Strength */}
      <div className="text-sm">
        Sentiment: <strong>{post.sentiment}</strong> (Strength: {post.strength?.toFixed(2) ?? 'N/A'}) {/* Format strength */}
      </div>
      {/* Tickers */}
      <div className="text-sm mt-1">
        Tickers: {post.tickers?.length > 0 ? (
          post.tickers.map((ticker, index) => (
            <React.Fragment key={ticker}>
              <button
                onClick={() => fetchStockStats(ticker)}
                className="text-blue-600 hover:underline focus:outline-none mx-1 px-1 bg-blue-50 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={tickerStats[ticker]?.loading} // Disable button while loading
              >
                {ticker}
              </button>
              {/* Display Stats Area - only show if loading, error, or data exists */}
              {tickerStats[ticker] && (tickerStats[ticker].loading || tickerStats[ticker].error || tickerStats[ticker].data) && (
                <div className="ml-4 mt-1 p-2 border rounded bg-gray-50 text-xs shadow-inner">
                  {tickerStats[ticker].loading && <p className="text-gray-600 animate-pulse">Loading stats for {ticker}...</p>}
                  {tickerStats[ticker].error && <p className="text-red-600">Error: {tickerStats[ticker].error}</p>}
                  {tickerStats[ticker].data && (
                    <ul className="list-disc list-inside space-y-1">
                      {Object.entries(tickerStats[ticker].data!).map(([key, value]) => (
                         value ? <li key={key}><strong className="font-medium">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> {value}</li> : null
                      ))}
                      {/* Show message if data object is empty */}
                      {Object.keys(tickerStats[ticker].data!).length === 0 && !tickerStats[ticker].loading && <li className="text-gray-500">No stats found for {ticker}.</li>}
                    </ul>
                  )}
                </div>
              )}
              {index < post.tickers.length - 1 ? ', ' : ''}
            </React.Fragment>
          ))
        ) : (
          <span className="text-gray-500">None mentioned</span>
        )}
      </div>
      {/* Keywords Section */}
      <div className="text-sm mt-1">
        <button
          onClick={toggleKeywords}
          className="text-blue-600 hover:underline text-sm mr-2 focus:outline-none"
        >
          {showKeywords ? 'Hide Keywords' : 'Show Keywords'} ({post.keywords?.length ?? 0})
        </button>
        {showKeywords && (
          <span className="text-gray-700">
            {post.keywords?.length > 0 ? post.keywords.join(", ") : <span className="text-gray-500">None identified</span>}
          </span>
        )}
      </div>
      {/* Reddit Link */}
      <a
        href={post.permalink}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-600 hover:underline text-sm mt-2 inline-block" /* Added margin top */
      >
        View on Reddit
      </a>
    </div>
  );
};

export default PostCard;
