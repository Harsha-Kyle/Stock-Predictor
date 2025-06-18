
import { PopularTicker } from './types';

export const POPULAR_TICKERS: PopularTicker[] = [
  { symbol: "AAPL", name: "Apple Inc." },
  { symbol: "GOOGL", name: "Alphabet Inc. (Google)" },
  { symbol: "MSFT", name: "Microsoft Corp." },
  { symbol: "TSLA", name: "Tesla, Inc." },
  { symbol: "AMZN", name: "Amazon.com, Inc." },
  { symbol: "META", name: "Meta Platforms, Inc." },
  { symbol: "RELIANCE.NS", name: "Reliance Industries Ltd." },
  { symbol: "TCS.NS", name: "Tata Consultancy Services Ltd." },
  { symbol: "INFY.NS", name: "Infosys Ltd." },
  { symbol: "NVDA", name: "NVIDIA Corporation" }
];

export const FORECAST_DAYS_OPTIONS: number[] = [7, 14, 30, 60, 90];

export const API_SIMULATION_DELAY = 1500; // ms