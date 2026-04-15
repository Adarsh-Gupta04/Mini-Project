let stockChart;

const symbolInput = document.getElementById("symbol");
const searchButton = document.getElementById("searchButton");
const loader = document.getElementById("loader");
const card = document.getElementById("card");
const errorBox = document.getElementById("error");

searchButton.addEventListener("click", getStock);
symbolInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    getStock();
  }
});

async function getStock() {
  const symbol = symbolInput.value.trim().toUpperCase();
  resetUI();

  if (!symbol) {
    showError("Please enter a stock symbol.");
    return;
  }

  showLoader(true);

  try {
    const response = await fetch(`/stock?symbol=${encodeURIComponent(symbol)}`);
    const data = await response.json();

    if (!response.ok || data.error) {
      throw new Error(data.error || "Unable to fetch stock data.");
    }

    const latest = data.latest;
    const previous = data.previous;
    const history = data.history || [];

    if (!latest || !history.length) {
      throw new Error("No historical data available.");
    }

    const changeAmount = latest.close - previous.close;
    const changePercent = data.changePercent || "0.00%";
    const changeText = `${changeAmount >= 0 ? "+" : ""}${changeAmount.toFixed(2)} (${changePercent})`;
    const avgVolume = formatVolume(average(history.slice(-10).map((item) => item.volume)));
    const rangeLabel = `$${latest.low.toFixed(2)} - $${latest.high.toFixed(2)}`;

    document.getElementById("stock-name").innerText = symbol;
    document.getElementById("symbol-tag").innerText = symbol;
    document.getElementById("stock-subtitle").innerText = data.metadata?.["1. Information"] || "Live market snapshot";
    document.getElementById("price").innerText = formatCurrency(latest.close);
    document.getElementById("price-small").innerText = formatCurrency(latest.close);
    document.getElementById("change").innerText = changeText;
    document.getElementById("open").innerText = formatCurrency(latest.open);
    document.getElementById("high").innerText = formatCurrency(latest.high);
    document.getElementById("low").innerText = formatCurrency(latest.low);
    document.getElementById("volume").innerText = formatVolume(latest.volume);
    document.getElementById("previous-close").innerText = formatCurrency(previous.close);
    document.getElementById("avg-volume").innerText = avgVolume;
    document.getElementById("range").innerText = rangeLabel;
    document.getElementById("chart-range").innerText = `Showing last ${history.length} trading days`;

    const badge = document.getElementById("change-badge");
    badge.innerText = changeText;
    badge.style.background = changeAmount < 0 ? "rgba(239, 68, 68, 0.14)" : "rgba(16, 185, 129, 0.12)";
    badge.style.color = changeAmount < 0 ? "#fecaca" : "#a7f3d0";

    renderChart(history);
    showLoader(false);
    card.classList.remove("hidden");
  } catch (error) {
    showLoader(false);
    showError(error.message || "Unable to fetch stock data.");
  }
}

function renderChart(history) {
  const chartContainer = document.getElementById("chart");
  chartContainer.innerHTML = "";

  const charts = window.LightweightCharts || window.lightweightCharts;
  if (!charts || typeof charts.createChart !== "function") {
    showError("Chart library failed to load. Refresh the page and try again.");
    return;
  }

  stockChart = charts.createChart(chartContainer, {
    width: chartContainer.clientWidth,
    height: 460,
    layout: {
      backgroundColor: "#020617",
      textColor: "#e2e8f0",
    },
    grid: {
      vertLines: { color: "rgba(148, 163, 184, 0.08)" },
      horzLines: { color: "rgba(148, 163, 184, 0.08)" },
    },
    rightPriceScale: {
      borderColor: "rgba(148, 163, 184, 0.18)",
    },
    timeScale: {
      borderColor: "rgba(148, 163, 184, 0.18)",
      timeVisible: true,
      secondsVisible: false,
    },
    crosshair: {
      mode: charts.CrosshairMode?.Normal || 0,
    },
  });

  if (typeof stockChart.addCandlestickSeries === "function") {
    const candleSeries = stockChart.addCandlestickSeries({
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderVisible: false,
      wickUpColor: "#22c55e",
      wickDownColor: "#ef4444",
    });

    candleSeries.setData(history.map((item) => ({
      time: item.time,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
    })));
  } else if (typeof stockChart.addLineSeries === "function") {
    const lineSeries = stockChart.addLineSeries({
      color: "#38bdf8",
      lineWidth: 2,
    });

    lineSeries.setData(history.map((item) => ({
      time: item.time,
      value: item.close,
    })));
  } else {
    showError("Your chart library version does not support series creation.");
    return;
  }

  stockChart.timeScale().fitContent();
}

function resetUI() {
  errorBox.classList.add("hidden");
  card.classList.add("hidden");
}

function showLoader(show) {
  loader.classList.toggle("hidden", !show);
}

function showError(message) {
  errorBox.innerText = `❌ ${message}`;
  errorBox.classList.remove("hidden");
}

function formatCurrency(value) {
  return `$${Number(value).toFixed(2)}`;
}

function formatVolume(value) {
  return Number(value).toLocaleString();
}

function average(values) {
  if (!values.length) return 0;
  return values.reduce((sum, current) => sum + current, 0) / values.length;
}

window.addEventListener("resize", () => {
  const chartContainer = document.getElementById("chart");
  if (stockChart && chartContainer) {
    stockChart.applyOptions({ width: chartContainer.clientWidth });
  }
});
