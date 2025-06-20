# app.py (Final Version with 10-Day Trend Advice)

import os
import traceback
import logging
from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import timedelta
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

# --- Lightweight Simulation Logic ---
def pseudo_random_py(seed_string, salt=0):
  h = 1779033703 ^ (len(seed_string) + salt)
  for char_code in [ord(c) for c in seed_string]:
    h = ((h ^ char_code) * 3432918353) & 0xFFFFFFFF
    h = (h << 13 | h >> 19) & 0xFFFFFFFF
  h = ((h ^ (h >> 16)) * 2246822507) & 0xFFFFFFFF
  h = ((h ^ (h >> 13)) * 3266489909) & 0xFFFFFFFF
  return ((h ^ (h >> 16)) & 0xFFFFFFFF) / 4294967296

# --- Advanced Charting Functions ---
def create_main_chart(historical_df, forecast_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=historical_df['ds'], y=historical_df['y'], mode='lines', name='Actual Price', line=dict(color='#3498db')))
    fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat'], mode='lines', name='Forecasted Price', line=dict(color='#2ecc71', dash='dash')))
    fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat_upper'], fill=None, mode='lines', line_color='rgba(46, 204, 113, 0.2)', name='Upper Bound', showlegend=False))
    fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat_lower'], fill='tonexty', mode='lines', line_color='rgba(46, 204, 113, 0.2)', name='Confidence Interval', showlegend=True))
    fig.update_layout(template='plotly_dark', xaxis_title='Date', yaxis_title='Stock Price', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=40, r=40, t=40, b=40))
    return fig.to_html(full_html=False, include_plotlyjs=False)

def create_backtest_chart(backtest_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=backtest_df['ds'], y=backtest_df['actual'], mode='lines+markers', name='Actual Price', line=dict(color='#3498db')))
    fig.add_trace(go.Scatter(x=backtest_df['ds'], y=backtest_df['predicted'], mode='lines+markers', name='Predicted Price (Backtest)', line=dict(color='#2ecc71')))
    fig.update_layout(template='plotly_dark', xaxis_title='Date', yaxis_title='Stock Price', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=40, r=40, t=40, b=40))
    return fig.to_html(full_html=False, include_plotlyjs=False)

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
        data = yf.download(ticker, period="1y", auto_adjust=True)
        if data.empty:
            return jsonify({"error": f"No data found for ticker '{ticker}'. Please check the symbol."}), 404
        
        df_history = pd.DataFrame({'ds': data.index, 'y': data['Close'].values.flatten()})
        df_history.dropna(inplace=True)
        df_history['ds'] = pd.to_datetime(df_history['ds']).dt.tz_localize(None)

        if len(df_history) < 10: # Need at least 10 days for the new advice logic
            return jsonify({"error": "Not enough historical data available for analysis."}), 400

        # --- High-Fidelity SIMULATED Forecast ---
        last_price = df_history['y'].iloc[-1]
        last_date = df_history['ds'].iloc[-1]
        
        future_data = []
        current_price = last_price
        for i in range(forecast_days_int):
            date = last_date + timedelta(days=i + 1)
            change = (pseudo_random_py(ticker, i) - 0.495) * (current_price * 0.03)
            current_price += change
            bound_percentage = 0.02 + (pseudo_random_py(ticker, i + 1000) * 0.03)
            future_data.append({
                'ds': date, 'yhat': current_price,
                'yhat_upper': current_price * (1 + bound_percentage),
                'yhat_lower': current_price * (1 - bound_percentage)
            })
        
        df_forecast_future = pd.DataFrame(future_data)
        
        last_historical_point = df_history.iloc[[-1]].copy()
        last_historical_point.rename(columns={'y': 'yhat'}, inplace=True)
        last_historical_point['yhat_upper'] = last_historical_point['yhat']
        last_historical_point['yhat_lower'] = last_historical_point['yhat']
        
        df_forecast_connected = pd.concat([last_historical_point, df_forecast_future], ignore_index=True)

        # --- SIMULATED Backtest ---
        df_history_for_backtest = df_history.tail(7).copy()
        backtest_predictions = []
        for i, row in df_history_for_backtest.iterrows():
            noise = (pseudo_random_py(ticker, i + 2000) - 0.5) * (row['y'] * 0.02)
            backtest_predictions.append(row['y'] + noise)
        
        df_backtest = pd.DataFrame({
            'ds': df_history_for_backtest['ds'],
            'actual': df_history_for_backtest['y'],
            'predicted': backtest_predictions
        })

        # --- Analysis and Response ---
        predicted_price_for_last_day = df_forecast_future['yhat'].iloc[-1] if not df_forecast_future.empty else last_price

        # --- FINAL FIX: Calculate advice based on the last 10 days of REAL data ---
        last_10_days = df_history.tail(10)
        start_price_10d = last_10_days['y'].iloc[0]
        end_price_10d = last_10_days['y'].iloc[-1]
        
        advice = "HOLD (Neutral)"
        if start_price_10d > 0:
            ten_day_change = (end_price_10d - start_price_10d) / start_price_10d
            # Use a slightly smaller threshold for more responsive advice
            if ten_day_change > 0.025:  # 2.5% increase over 10 days
                advice = "BUY (Upward Trend)"
            elif ten_day_change < -0.025: # 2.5% decrease over 10 days
                advice = "SELL (Downward Trend)"

        future_forecast_table_data = df_forecast_future[['ds', 'yhat']].copy()
        future_forecast_table_data['ds'] = future_forecast_table_data['ds'].dt.strftime('%Y-%m-%d')
        future_forecast_table_data = future_forecast_table_data.to_dict(orient='records')
        
        df_history_sliced = df_history.tail(90)
        main_chart_html = create_main_chart(df_history_sliced, df_forecast_connected)
        backtest_chart_html = create_backtest_chart(df_backtest)

        return jsonify({
            "ticker": ticker, "forecastDays": forecast_days_int,
            "predictedPriceForLastDay": round(predicted_price_for_last_day, 2),
            "advice": advice, "futureForecastTableData": future_forecast_table_data,
            "mainChartHtml": main_chart_html, "backtestChartHtml": backtest_chart_html,
        })

    except Exception as e:
        app.logger.error(f"An error occurred for ticker {ticker}:")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred. This has been logged."}), 500

@app.route('/')
def home():
    return render_template('index.html', popular_tickers=POPULAR_TICKERS_PY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
