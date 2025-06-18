
import { StockDataPoint, ForecastDataPoint, CombinedChartDataPoint, BacktestDataPoint, StockPredictionResponse, InvestmentAdvice } from '../types';
import { API_SIMULATION_DELAY, POPULAR_TICKERS } from '../constants';

const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0];
};

// Simple pseudo-random number generator for consistency based on ticker
const pseudoRandom = (seedString: string, salt: number = 0): number => {
  let h = 1779033703 ^ seedString.length + salt;
  for (let i = 0; i < seedString.length; i++) {
    h = Math.imul(h ^ seedString.charCodeAt(i), 3432918353);
    h = h << 13 | h >>> 19;
  }
  h = Math.imul(h ^ (h >>> 16), 2246822507);
  h = Math.imul(h ^ (h >>> 13), 3266489909);
  return ((h ^= h >>> 16) >>> 0) / 4294967296; // Normalize to 0-1
};


export const fetchStockDataAndForecast = (
  ticker: string,
  forecastDays: number
): Promise<StockPredictionResponse> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const knownTicker = POPULAR_TICKERS.find(t => t.symbol.toUpperCase() === ticker.toUpperCase());
      if (!knownTicker && Math.random() < 0.2) { // 20% chance of "invalid ticker" for unknown ones
         reject(new Error(`Invalid ticker symbol: ${ticker} or no data found. Please try a known ticker.`));
         return;
      }

      const historicalData: StockDataPoint[] = [];
      const fullForecastData: ForecastDataPoint[] = [];
      const mainChartData: CombinedChartDataPoint[] = [];
      const backtestChartData: BacktestDataPoint[] = [];

      const today = new Date();
      let currentDate = new Date(today);
      currentDate.setDate(today.getDate() - 365); // 1 year of historical data

      // Generate historical data
      let lastPrice = pseudoRandom(ticker, 1) * 300 + 50; // Base price between 50-350
      for (let i = 0; i < 365; i++) {
        const dateStr = formatDate(currentDate);
        const change = (pseudoRandom(ticker, i + 100) - 0.49) * (lastPrice * 0.05); // Daily change up to 5%
        lastPrice += change;
        lastPrice = Math.max(lastPrice, 1); // Price can't be negative

        const actualPrice = parseFloat(lastPrice.toFixed(2));
        historicalData.push({ ds: dateStr, y: actualPrice });
        mainChartData.push({ ds: dateStr, actual: actualPrice });
        
        currentDate.setDate(currentDate.getDate() + 1);
      }
      
      // Simulate Prophet-like forecast for historical period (for backtesting and chart continuity)
      // This is a very simplified simulation
      const historicalForecastSeed = 2000;
      historicalData.forEach((point, index) => {
        const forecastNoise = (pseudoRandom(ticker, index + historicalForecastSeed) - 0.5) * (point.y * 0.05); // +/- 5% error
        const yhat = parseFloat((point.y + forecastNoise).toFixed(2));
        const yhat_lower = parseFloat((yhat * (1 - (0.03 + pseudoRandom(ticker, index + historicalForecastSeed + 1) * 0.05))).toFixed(2)); // 3-8% lower bound
        const yhat_upper = parseFloat((yhat * (1 + (0.03 + pseudoRandom(ticker, index + historicalForecastSeed + 2) * 0.05))).toFixed(2)); // 3-8% upper bound
        
        fullForecastData.push({ ds: point.ds, yhat, yhat_lower, yhat_upper });
        
        // Update mainChartData with these "historical" predictions for continuity if needed
        // but typically Prophet's forecast component in chart starts after historical.
        // For this example, we'll merge them in mainChartData later
      });


      // Generate future forecast data
      let lastForecastPrice = historicalData[historicalData.length - 1].y;
      const futureForecastSeed = 3000;
      const futureForecastTableData: { ds: string, yhat: number }[] = [];

      currentDate = new Date(today); // Reset to today for forecast start
      currentDate.setDate(currentDate.getDate() + 1); // Start forecast from tomorrow

      for (let i = 0; i < forecastDays; i++) {
        const dateStr = formatDate(currentDate);
        // Trend factor: slightly positive by default, can be influenced by ticker string
        const trendFactor = (pseudoRandom(ticker, i + futureForecastSeed) - 0.48) * (lastForecastPrice * 0.03); 
        lastForecastPrice += trendFactor;
        lastForecastPrice = Math.max(lastForecastPrice, 1);

        const yhat = parseFloat(lastForecastPrice.toFixed(2));
        const boundPercentage = 0.05 + pseudoRandom(ticker, i + futureForecastSeed + 1) * 0.10; // 5-15% for bounds
        const yhat_lower = parseFloat((yhat * (1 - boundPercentage)).toFixed(2));
        const yhat_upper = parseFloat((yhat * (1 + boundPercentage)).toFixed(2));

        fullForecastData.push({ ds: dateStr, yhat, yhat_lower, yhat_upper });
        futureForecastTableData.push({ ds: dateStr, yhat });
        
        mainChartData.push({ 
            ds: dateStr, 
            forecast: yhat, 
            lowerBound: yhat_lower, 
            upperBound: yhat_upper 
        });

        currentDate.setDate(currentDate.getDate() + 1);
      }

      // Prepare backtest data (last 7 days of historical)
      const historicalDataForBacktest = historicalData.slice(-7);
      historicalDataForBacktest.forEach(histPoint => {
        const correspondingForecast = fullForecastData.find(f => f.ds === histPoint.ds);
        if (correspondingForecast) {
          backtestChartData.push({
            ds: histPoint.ds,
            actual: histPoint.y,
            predicted: correspondingForecast.yhat
          });
        }
      });
      
      // Merge historical forecasts into mainChartData for the historical part
       mainChartData.forEach(mcPoint => {
        if (mcPoint.actual !== undefined && mcPoint.forecast === undefined) { // If it's a historical point not yet having forecast data
            const ffPoint = fullForecastData.find(ff => ff.ds === mcPoint.ds);
            if (ffPoint) {
                mcPoint.forecast = ffPoint.yhat; // This shows prophet's fit on historical
                mcPoint.lowerBound = ffPoint.yhat_lower;
                mcPoint.upperBound = ffPoint.yhat_upper;
            }
        }
      });


      const predictedPriceForLastDay = futureForecastTableData.length > 0 ? futureForecastTableData[futureForecastTableData.length - 1].yhat : 0;

      // Investment advice logic
      let advice = InvestmentAdvice.HOLD;
      if (historicalData.length > 0 && futureForecastTableData.length > 0) {
        const lastActual = historicalData[historicalData.length - 1].y;
        const firstFuturePred = futureForecastTableData[0].yhat; // Prediction for tomorrow
        const change = (firstFuturePred - lastActual) / lastActual;
        
        // Use a slightly different logic for advice: compare last actual to avg of next few days forecast
        const avgNextFewDaysForecast = futureForecastTableData.slice(0, Math.min(7, futureForecastTableData.length))
                                       .reduce((sum, item) => sum + item.yhat, 0) / Math.min(7, futureForecastTableData.length);
        const overallChange = (avgNextFewDaysForecast - lastActual) / lastActual;


        if (overallChange > 0.03) { // If avg of next week is >3% higher
          advice = InvestmentAdvice.BUY;
        } else if (overallChange < -0.03) { // If avg of next week is >3% lower
          advice = InvestmentAdvice.SELL;
        }
      }

      resolve({
        ticker,
        forecastDays,
        historicalData,
        fullForecastData,
        futureForecastTableData,
        predictedPriceForLastDay,
        advice,
        backtestChartData,
        mainChartData
      });
    }, API_SIMULATION_DELAY);
  });
};