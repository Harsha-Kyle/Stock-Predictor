# app.py (Fast Hybrid Version - Live History, Simulated Forecast)

import os
import traceback
import logging
from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
import random

# --- Basic App and Logging Setup ---
gunicorn_logger = logging.getLogger('gunicorn.error')
app = Flask(__name__)
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

# --- Predefined Data ---
POPULAR_TICKERS_PY = [
    {"symbol": "AAPL", "name": "Apple Inc."}, {"symbol": "GOOGL", "name": "Alphabet Inc. (Google)"},
    {"symbol": "MSFT", "name": "Microsoft Corp."}, {"symbol": "TSLA", "name": "Tesla, Inc."},
    {"symbol": "AMZN", "name": "Amazon.com, Inc."}, {"symbol": "META", "name": "Meta Platforms, Inc."},
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries Ltd."}, {"symbol": "TCS.NS", "name": "Tata Consultancy Services Ltd."},
    {"symbol": "INFY.NS", "name": "Infosys Ltd."}, {"symbol": "NVDA", "name": "NVIDIA Corporation"}
]

# --- Charting Functions (Unchanged) ---
def create_main_chart(df, forecast_df):
    """Creates the main Plotly chart with actual and forecast data."""
    fig = go.Figure()
    # Actual prices from yfinance
    fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], mode='lines', name='Actual Price', line=dict(color='#3498db')))
    # Simulated forecast prices
    fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat'], mode='lines', name='Forecasted Price (Simulated)', line=dict(color='#2ecc71', dash='dash')))
    
    fig.update_layout(template='plotly_dark', xaxis_title='Date', yaxis_title='Stock Price', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=40, r=40, t=40, b=40))
    return fig.to_html(full_html=False, include_plotlyjs=False)

# --- Lightweight Simulation Logic (from the very first version) ---
def pseudo_random_py(seed_string, salt=0):
  h = 1779033703 ^ (len(seed_string) + salt)
  for char_code in [ord(c) for c in seed_string]:
    h = ((h ^ char_code) * 3432918353) & 0xFFFFFFFF
    h = (h << 13 | h >> 19) & 0xFFFFFFFF
  h = ((h ^ (h >> 16)) * 2246822507) & 0xFFFFFFFF
  h = ((h ^ (h >> 13)) * 3266489909) & 0xFFFFFFFF
  return ((h ^ (h >> 16)) & 0xFFFFFFFF) / 4294967296

# --- API Endpoint and Main Logic ---
@app.route('/api/predict', methods=['GET'])
def predict():
    ticker = request.args.get('ticker')
    days_str = request.args.get('days')

    if not ticker or not days_str:
        return jsonify({"error": "Missing ticker or days parameter"}), 400
    
    try:
        forecast_days_int = int(days_str)
    except ValueError:
        return jsonify({"error": "Invalid days parameter, must be an integer"}), 400

    try:
        # STEP 1: Fetch REAL historical data (this part is fast)
        data = yf.download(ticker, period="1y", auto_adjust=True)
        if data.empty:
            return jsonify({"error": f"No data found for ticker '{ticker}'. Please check the symbol."}), 404
        
        # Prepare historical data for charting
        df_history = pd.DataFrame({'ds': data.index, 'y': data['Close'].values.flatten()})
        df_history.dropna(inplace=True)
        df_history['ds'] = pd.to_datetime(df_history['ds']).dt.tz_localize(None)

        if len(df_history) < 1:
            return jsonify({"error": "Not enough historical data available."}), 400
        
        # STEP 2: Generate a FAST SIMULATED forecast (instead of slow Prophet)
        last_price = df_history['y'].iloc[-1]
        last_date = df_history['ds'].iloc[-1]
        
        future_dates = []
        future_prices = []
        
        current_price = last_price
        for i in range(forecast_days_int):
            current_date = last_date + timedelta(days=i + 1)
            change = (pseudo_random_py(ticker, i) - 0.48) * (current_price * 0.03)
            current_price += change
            future_dates.append(current_date)
            future_prices.append(current_price)
        
        df_forecast = pd.DataFrame({'ds': future_dates, 'yhat': future_prices})
        
        # --- Analysis and Response ---
        predicted_price_for_last_day = df_forecast['yhat'].iloc[-1]
        last_actual = last_price
        avg_next_few_days_forecast = df_forecast['yhat'].head(7).mean()

        overall_change = (avg_next_few_days_forecast - last_actual) / last_actual
        if overall_change > 0.03: advice = "BUY (Upward Trend)"
        elif overall_change < -0.03: advice = "SELL (Downward Trend)"
        else: advice = "HOLD (Neutral)"

        future_forecast_table = df_forecast.copy()
        future_forecast_table['ds'] = future_forecast_table['ds'].dt.strftime('%Y-%m-%d')
        future_forecast_table_data = future_forecast_table.to_dict(orient='records')
        
        main_chart_html = create_main_chart(df_history, df_forecast)
        # Backtest chart is omitted as it requires a real model fit.

        return jsonify({
            "ticker": ticker, "forecastDays": forecast_days_int,
            "predictedPriceForLastDay": round(predicted_price_for_last_day, 2),
            "advice": advice, "futureForecastTableData": future_forecast_table_data,
            "mainChartHtml": main_chart_html,
            "backtestChartHtml": "<div>Backtesting requires the full Prophet model and is disabled in this fast--mode.</div>",
        })

    except Exception as e:
        app.logger.error(f"An error occurred for ticker {ticker}:")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred. This has been logged."}), 500

# --- Main HTML Route ---
@app.route('/')
def home():
    return render_template('index.html', popular_tickers=POPULAR_TICKERS_PY)

# --- Local Development Entry Point ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
