
import React, { useState } from 'react';
import { POPULAR_TICKERS, FORECAST_DAYS_OPTIONS } from '../constants';
import { PopularTicker } from '../types';

interface StockFormProps {
  onSubmit: (ticker: string, days: number) => void;
  isLoading: boolean;
}

export const StockForm: React.FC<StockFormProps> = ({ onSubmit, isLoading }) => {
  const [ticker, setTicker] = useState<string>('');
  const [days, setDays] = useState<number>(FORECAST_DAYS_OPTIONS[0]);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (ticker.trim()) {
      onSubmit(ticker.trim().toUpperCase(), days);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="ticker-input" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Stock Ticker Symbol
        </label>
        <div className="relative">
          <input
            id="ticker-input"
            type="text"
            list="tickers-datalist"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            placeholder="e.g., AAPL, RELIANCE.NS"
            required
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-primary focus:border-primary dark:bg-gray-700 dark:text-white"
            aria-label="Stock Ticker Symbol"
          />
          <datalist id="tickers-datalist">
            {POPULAR_TICKERS.map((t: PopularTicker) => (
              <option key={t.symbol} value={t.symbol}>
                {t.name}
              </option>
            ))}
          </datalist>
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5 text-gray-400">
              <path fillRule="evenodd" d="M9 3.5a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11ZM2 9a7 7 0 1 1 12.452 4.391l3.328 3.329a.75.75 0 1 1-1.06 1.06l-3.329-3.328A7 7 0 0 1 2 9Z" clipRule="evenodd" />
            </svg>
          </div>
        </div>
      </div>

      <div>
        <label htmlFor="days-select" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Forecast Period (Days)
        </label>
        <select
          id="days-select"
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-primary focus:border-primary dark:bg-gray-700 dark:text-white"
          aria-label="Forecast Period in Days"
        >
          {FORECAST_DAYS_OPTIONS.map((d) => (
            <option key={d} value={d}>
              {d} Days
            </option>
          ))}
        </select>
      </div>

      <button
        type="submit"
        disabled={isLoading || !ticker.trim()}
        className="w-full flex items-center justify-center px-6 py-3 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-primary hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? (
          <>
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Predicting...
          </>
        ) : (
          'Predict Stock Price'
        )}
      </button>
    </form>
  );
};