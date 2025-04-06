import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import HomePage from "../app/page";

global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () =>
      Promise.resolve([
        {
          id: "abc123",
          title: "Test Post",
          subreddit: "wallstreetbets",
          author: "testuser",
          sentiment: "Positive",
          strength: 0.9,
          tickers: ["TSLA", "AAPL"],
          keywords: ["bullish", "growth"],
          permalink: "https://reddit.com/testpost",
        },
      ]),
  })
) as jest.Mock;

describe("HomePage sentiment feed", () => {
  it("renders posts with sentiment data", async () => {
    render(<HomePage />);

    await waitFor(() => {
      expect(screen.getByText("Test Post")).toBeInTheDocument();
      expect(screen.getByText(/Sentiment:/)).toHaveTextContent("Positive");
      expect(screen.getByText(/Tickers:/)).toHaveTextContent("TSLA, AAPL");
      expect(screen.getByText(/Keywords:/)).toHaveTextContent("bullish, growth");
      expect(screen.getByText("View on Reddit")).toHaveAttribute("href", "https://reddit.com/testpost");
    });
  });
});
