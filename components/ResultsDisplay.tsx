import React from 'react';
import { StockPredictionResponse, InvestmentAdvice, BacktestDataPoint, CombinedChartDataPoint } from '../types';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceArea } from 'recharts';

interface ResultsDisplayProps {
  data: StockPredictionResponse;
  getAdviceColor: (advice: InvestmentAdvice) => string;
}

const CustomTooltip: React.FC<any> = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white dark:bg-gray-800 p-3 shadow-lg rounded-md border border-gray-200 dark:border-gray-700">
        <p className="label font-semibold text-gray-700 dark:text-gray-300">{`Date: ${label}`}</p>
        {payload.map((pld: any, index: number) => (
          <p key={index} style={{ color: pld.color }} className="text-sm">
            {`${pld.name}: ₹${pld.value?.toFixed(2)}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};


export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ data, getAdviceColor }) => {
  const { ticker, forecastDays, predictedPriceForLastDay, advice, futureForecastTableData, mainChartData, backtestChartData } = data;

  const formatCurrency = (value: number) => `₹${value.toFixed(2)}`;

  const historicalDataEndIndex = mainChartData.findIndex(d => d.forecast !== undefined && d.forecast !== null);


  return (
    <div className="space-y-8">
      <section id="summary" className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
        <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-1">
          Prediction Summary
        </h2>
        <p className="text-md text-gray-500 dark:text-gray-400 mb-2">
          Results for: <span className="font-semibold text-primary">{ticker}</span>
        </p>
        <p className="text-lg text-gray-600 dark:text-gray-300">
          Forecast Period: <span className="font-medium">{forecastDays} Days</span>
        </p>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <p className="text-sm text-gray-500 dark:text-gray-400">Predicted Price (End of Period)</p>
            <p className="text-3xl font-bold text-gray-800 dark:text-white">{formatCurrency(predictedPriceForLastDay)}</p>
          </div>
          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <p className="text-sm text-gray-500 dark:text-gray-400">Investment Suggestion</p>
            <p className={`text-3xl font-bold ${getAdviceColor(advice)}`}>{advice}</p>
          </div>
        </div>
      </section>

      <section id="forecast-chart" className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
        <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Price Forecast Chart</h3>
        <div className="w-full h-96">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mainChartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.2} />
              <XAxis dataKey="ds" tick={{ fontSize: 12, fill: '#6b7280' }} />
              <YAxis tickFormatter={(value) => `₹${value}`} tick={{ fontSize: 12, fill: '#6b7280' }} domain={['auto', 'auto']}/>
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line type="monotone" dataKey="actual" name="Actual Price" stroke="#3b82f6" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="forecast" name="Forecasted Price" stroke="#f59e0b" strokeWidth={2} dot={false} />
              {historicalDataEndIndex > 0 && (
                 <ReferenceArea x1={mainChartData[0].ds} x2={mainChartData[historicalDataEndIndex -1].ds} strokeOpacity={0.3} label={{value: "Historical Data", position:"insideTopLeft", fill:"#6b7280", fontSize:10, dy:-10 }} />
              )}
              {historicalDataEndIndex > 0 && historicalDataEndIndex < mainChartData.length && (
                 <ReferenceArea x1={mainChartData[historicalDataEndIndex].ds} x2={mainChartData[mainChartData.length -1].ds} strokeOpacity={0.3} label={{value: "Forecast Period", position:"insideTopLeft", fill:"#6b7280", fontSize:10, dy:-10 }}/>
              )}
              <Line type="monotone" dataKey="lowerBound" name="Lower Bound" stroke="#a1a1aa" strokeWidth={1} strokeDasharray="5 5" dot={false} />
              <Line type="monotone" dataKey="upperBound" name="Upper Bound" stroke="#a1a1aa" strokeWidth={1} strokeDasharray="5 5" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section id="forecast-table" className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
        <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">{forecastDays}-Day Forecast Table</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Predicted Price</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {futureForecastTableData.map((row) => (
                <tr key={row.ds}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{row.ds}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{formatCurrency(row.yhat)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      
      {backtestChartData && backtestChartData.length > 0 && (
        <section id="backtest-chart" className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
          <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Backtest (Last 7 Days)</h3>
          <div className="w-full h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={backtestChartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.2} />
                <XAxis dataKey="ds" tick={{ fontSize: 12, fill: '#6b7280' }} />
                <YAxis tickFormatter={(value) => `₹${value}`} tick={{ fontSize: 12, fill: '#6b7280' }} domain={['auto', 'auto']}/>
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Line type="monotone" dataKey="actual" name="Actual Price" stroke="#3b82f6" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="predicted" name="Predicted Price (Backtest)" stroke="#10b981" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>
      )}
    </div>
  );
};