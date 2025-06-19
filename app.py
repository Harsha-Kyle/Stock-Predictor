# app.py (Final, Resilient Version)

import os
from flask import Flask, render_template, request, jsonify
import yfinance as yf
from prophet import Prophet
import pandas as pd
import plotly.graph_objs as go
import traceback  # Import the traceback module for detailed error logging

# A predefined list of popular tickers for the search suggestion
POPULAR_TICKERS_PY = [
    {"symbol": "AAPL", "name": "Apple Inc."},
    {"symbol": "GOOGL", "name": "Alphabet Inc. (Google)"},
    {"symbol": "MSFT", "name": "Microsoft Corp."},
    {"symbol": "TSLA", "name": "Tesla, Inc."},
    {"symbol": "AMZN", "name": "Amazon.com, Inc."},
    {"symbol": "META", "name": "Meta Platforms, Inc."},
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries Ltd."},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services Ltd."},
    {"symbol": "INFY.NS", "name": "Infosys Ltd."},
    {"symbol": "NVDA", "name": "NVIDIA Corporation"}
]

app = Flask(__name__)

# Chart creation functions remain the same
def create_main_chart(df, forecast):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], mode='lines', name='Actual Price', line=dict(color='#3498db')))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecasted Price', line=dict(color='#2ecc71', dash='dash')))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill=None, mode='lines', line_color='rgba(46, 204, 113, 0.2)', name='Upper Bound'))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill='tonexty', mode='lines', line_color='rgba(46, 204, 113, 0.2)', name='Lower Bound'))
    fig.update_layout(template='plotly_dark', xaxis_title='Date', yaxis_title='Stock Price', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=40, r=40, t=40, b=40))
    return fig.to_html(full_html=False, include_plotlyjs=False)

def create_backtest_chart(df, forecast):
    merged_df = pd.merge(df, forecast[['ds', 'yhat']], on='ds')
    backtest_df = merged_df.tail(7)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=backtest_df['ds'], y=backtest_df['y'], mode='lines+markers', name='Actual Price', line=dict(color='#3498db')))
    fig.add_trace(go.Scatter(x=backtest_df['ds'], y=backtest_df['yhat'], mode='lines+markers', name='Predicted Price (Backtest)', line=dict(color='#2ecc71')))
    fig.update_layout(template='plotly_dark', xaxis_title='Date', yaxis_title='Stock Price', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=40, r=40, t=40, b=40))
    return fig.to_html(full_html=False, include_plotlyjs=False)

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
        data = yf.download(ticker, period="1y")
        if data.empty:
            return jsonify({"error": f"No data found for ticker '{ticker}'. Please check the symbol."}), 404
        
        df = data.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
        
        # --- THE NEW, MORE ROBUST FIX ---
        # 1. Drop any rows with missing values (NaN) which yfinance can return.
        df.dropna(inplace=True)
        
        # 2. Ensure the date column is in the correct datetime format.
        df['ds'] = pd.to_datetime(df['ds'])

        # 3. Check for sufficient data AFTER cleaning. Prophet needs at least 2 data points.
        if len(df) < 2:
            return jsonify({"error": f"Not enough historical data for '{ticker}' to make a forecast after cleaning."}), 400
        # --- END OF FIX ---

        model = Prophet()
        model.fit(df)
        
        future = model.make_future_dataframe(periods=forecast_days_int)
        forecast = model.predict(future)
        
        # The rest of the logic remains the same
        predicted_price_for_last_day = forecast['yhat'].iloc[-1]
        last_actual = df['y'].iloc[-1]
        avg_next_few_days_forecast = forecast['yhat'].iloc[-forecast_days_int:].head(7).mean()
        overall_change = (avg_next_few_days_forecast - last_actual) / last_actual
        
        if overall_change > 0.03: advice = "BUY (Upward Trend)"
        elif overall_change < -0.03: advice = "SELL (Downward Trend)"
        else: advice = "HOLD (Neutral)"

        future_forecast_table = forecast[forecast['ds'] > df['ds'].max()][['ds', 'yhat']]
        future_forecast_table['ds'] = future_forecast_table['ds'].dt.strftime('%Y-%m-%d')
        future_forecast_table_data = future_forecast_table.to_dict(orient='records')
        
        main_chart_html = create_main_chart(df, forecast)
        backtest_chart_html = create_backtest_chart(df, forecast)

        return jsonify({
            "ticker": ticker,
            "forecastDays": forecast_days_int,
            "predictedPriceForLastDay": round(predicted_price_for_last_day, 2),
            "advice": advice,
            "futureForecastTableData": future_forecast_table_data,
            "mainChartHtml": main_chart_html,
            "backtestChartHtml": backtest_chart_html,
        })

    except Exception as e:
        # --- ENHANCED ERROR LOGGING ---
        # This will print the full error traceback to your Render logs for easier debugging.
        print(f"An error occurred for ticker {ticker}:")
        print(traceback.format_exc())
        return jsonify({"error": "An internal error occurred. Please check the server logs."}), 500

@app.route('/')
def home():
    return render_template('index.html', popular_tickers=POPULAR_TICKERS_PY)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
