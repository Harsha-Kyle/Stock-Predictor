
export interface StockDataPoint {
  ds: string; // Date string YYYY-MM-DD
  y: number;  // Actual price
}

export interface ForecastDataPoint {
  ds: string; // Date string YYYY-MM-DD
  yhat: number;
  yhat_lower: number;
  yhat_upper: number;
}

export interface CombinedChartDataPoint {
  ds: string;
  actual?: number;
  forecast?: number;
  lowerBound?: number;
  upperBound?: number;
}

export interface BacktestDataPoint {
  ds: string;
  actual: number;
  predicted: number;
}

export interface StockPredictionResponse {
  ticker: string;
  forecastDays: number;
  historicalData: StockDataPoint[];
  fullForecastData: ForecastDataPoint[]; // Includes historical and future predictions
  futureForecastTableData: { ds: string, yhat: number }[];
  predictedPriceForLastDay: number;
  advice: InvestmentAdvice;
  backtestChartData: BacktestDataPoint[];
  mainChartData: CombinedChartDataPoint[];
}

export enum InvestmentAdvice {
  BUY = "BUY (Upward Trend)",
  SELL = "SELL (Downward Trend)",
  HOLD = "HOLD (Neutral)",
  NONE = ""
}

export interface PopularTicker {
  symbol: string;
  name: string;
}