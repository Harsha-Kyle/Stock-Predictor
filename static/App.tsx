
import React, { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { StockForm } from './components/StockForm';
import { ResultsDisplay } from './components/ResultsDisplay';
import { Loader } from './components/Loader';
import { ErrorDisplay } from './components/ErrorDisplay';
import { StockPredictionResponse, InvestmentAdvice } from './types';
import { fetchStockDataAndForecast } from './services/stockService';

const App: React.FC = () => {
  const [predictionData, setPredictionData] = useState<StockPredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [currentTicker, setCurrentTicker] = useState<string>('');
  const [currentForecastDays, setCurrentForecastDays] = useState<number>(7);

  const handlePrediction = useCallback(async (ticker: string, days: number) => {
    setIsLoading(true);
    setError(null);
    setPredictionData(null);
    setCurrentTicker(ticker);
    setCurrentForecastDays(days);

    try {
      const data = await fetchStockDataAndForecast(ticker, days);
      setPredictionData(data);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unknown error occurred.');
      }
      setPredictionData(null); 
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getAdviceColor = (advice: InvestmentAdvice): string => {
    switch (advice) {
      case InvestmentAdvice.BUY:
        return 'text-green-500';
      case InvestmentAdvice.SELL:
        return 'text-red-500';
      case InvestmentAdvice.HOLD:
      default:
        return 'text-gray-700 dark:text-gray-300';
    }
  };

  return (
    <div className="min-h-screen bg-base-100 text-neutral flex flex-col items-center selection:bg-primary selection:text-white">
      <Header />
      <main className="container mx-auto p-4 md:p-8 flex-grow w-full max-w-6xl">
        <section id="input-section" className="mb-8 p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
          <StockForm onSubmit={handlePrediction} isLoading={isLoading} />
        </section>

        {isLoading && <Loader />}
        {error && !isLoading && <ErrorDisplay message={error} />}
        
        {predictionData && !isLoading && !error && (
          <ResultsDisplay 
            data={predictionData} 
            getAdviceColor={getAdviceColor}
          />
        )}

        {!isLoading && !error && !predictionData && (
          <div className="text-center p-10 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
            <h2 className="text-2xl font-semibold text-gray-700 dark:text-gray-300 mb-4">Welcome to Stock Predictor</h2>
            <p className="text-gray-500 dark:text-gray-400">
              Enter a stock ticker symbol and select a forecast period to get started.
            </p>
            <img src="https://picsum.photos/seed/markets/600/300" alt="Stock Market" className="mt-6 rounded-lg shadow-md mx-auto opacity-75" />
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
};

export default App;
