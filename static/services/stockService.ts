
import { StockPredictionResponse } from '../types';
// API_SIMULATION_DELAY and POPULAR_TICKERS from constants are no longer directly used here
// as the logic is now backend-driven.

export const fetchStockDataAndForecast = async (
  ticker: string,
  forecastDays: number
): Promise<StockPredictionResponse> => {
  const response = await fetch(`/api/predict?ticker=${encodeURIComponent(ticker)}&days=${forecastDays}`);
  
  if (!response.ok) {
    let errorMessage = `API Error: ${response.status}`;
    try {
      // Try to parse a JSON error response from the backend
      const errorData = await response.json();
      errorMessage = errorData.error || errorData.message || errorMessage;
    } catch (e) {
      // If parsing fails or no JSON body, use the status text or the generic message
      errorMessage = response.statusText || errorMessage;
      if (response.status === 404 && !errorMessage.includes(ticker)) {
        // More specific message for 404 if not already detailed by backend
        errorMessage = `Data not found for ticker: ${ticker}. It might be an invalid symbol.`;
      }
    }
    throw new Error(errorMessage);
  }
  
  const data = await response.json();
  // Ensure the advice field from backend matches one of the InvestmentAdvice enum values.
  // The backend currently sends strings like "BUY (Upward Trend)" which match the enum values.
  return data as StockPredictionResponse;
};
