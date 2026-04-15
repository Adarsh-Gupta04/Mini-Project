const express = require("express");
const axios = require("axios");
require("dotenv").config();
const path = require("path");

const app = express();

// Serve static files
app.use(express.static(path.join(__dirname, "public")));

// Home route (index.html open hoga)
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

// Stock API
app.get("/stock", async (req, res) => {
  const symbol = req.query.symbol;

  if (!symbol) {
    return res.status(400).json({ error: "Please provide a stock symbol." });
  }

  const normalizedSymbol = symbol.trim().toUpperCase();
  const encodedSymbol = encodeURIComponent(normalizedSymbol);
  const yahooUrl = `https://query1.finance.yahoo.com/v8/finance/chart/${encodedSymbol}?interval=1d&range=6mo&events=div%2Csplit`;

  try {
    const response = await axios.get(yahooUrl);
    const chart = response.data?.chart;

    if (!chart) {
      return res.status(400).json({ error: "No chart data returned from Yahoo Finance." });
    }

    if (chart.error) {
      return res.status(400).json({ error: chart.error.description || "Invalid stock symbol." });
    }

    const result = chart.result?.[0];

    if (!result) {
      return res.status(400).json({ error: "Invalid stock symbol or no chart data returned." });
    }

    const timestamps = result.timestamp || [];
    const quote = result.indicators?.quote?.[0];

    if (!quote || !Array.isArray(timestamps) || !quote.close) {
      return res.status(400).json({ error: "Unable to load historical pricing data." });
    }

    const history = timestamps
      .map((timestamp, index) => ({
        time: new Date(timestamp * 1000).toISOString().slice(0, 10),
        open: Number(quote.open?.[index]),
        high: Number(quote.high?.[index]),
        low: Number(quote.low?.[index]),
        close: Number(quote.close?.[index]),
        volume: Number(quote.volume?.[index]),
      }))
      .filter((item) =>
        Number.isFinite(item.open) &&
        Number.isFinite(item.high) &&
        Number.isFinite(item.low) &&
        Number.isFinite(item.close)
      )
      .slice(-100);

    if (!history.length) {
      return res.status(400).json({ error: "No valid historical trading data was returned." });
    }

    const latest = history[history.length - 1];
    const previous = history[history.length - 2] || latest;
    const changeAmount = Number((latest.close - previous.close).toFixed(2));
    const changePercent = previous.close
      ? `${((changeAmount / previous.close) * 100).toFixed(2)}%`
      : "0.00%";

    res.json({
      symbol: normalizedSymbol,
      latest,
      previous,
      change: changeAmount,
      changePercent,
      history: history.slice(-50),
      metadata: {
        symbol: normalizedSymbol,
        exchangeName: result.meta?.exchangeName || "",
        currency: result.meta?.currency || "",
      },
    });
  } catch (error) {
    console.error("Stock API error:", error.response?.data || error.message);
    const message =
      error.response?.data?.chart?.error?.description ||
      error.response?.data?.error ||
      error.message ||
      "Unable to fetch stock data.";
    res.status(502).json({ error: message });
  }
});

// Start server (ALWAYS last)
app.listen(3000, () => console.log("Server running on port 3000"));
