from flask import Flask, render_template, request, jsonify, send_from_directory
import random
from datetime import datetime, timedelta

# (Simulated data generation - ported from TypeScript)
# In a real scenario, this would use yfinance, prophet, etc.
# For simplicity, we're keeping the ported simulation logic.

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

# Investment Advice Enum (mirrors TypeScript)
class InvestmentAdvice:
  BUY = "BUY (Upward Trend)"
  SELL = "SELL (Downward Trend)"
  HOLD = "HOLD (Neutral)"
  NONE = ""

def format_date_py(date_obj):
  return date_obj.strftime('%Y-%m-%d')

def pseudo_random_py(seed_string, salt=0):
  h = 1779033703 ^ (len(seed_string) + salt)
  for char_code in [ord(c) for c in seed_string]:
    h = ((h ^ char_code) * 3432918353) & 0xFFFFFFFF
    h = (h << 13 | h >> 19) & 0xFFFFFFFF
  h = ((h ^ (h >> 16)) * 2246822507) & 0xFFFFFFFF
  h = ((h ^ (h >> 13)) * 3266489909) & 0xFFFFFFFF
  return ((h ^ (h >> 16)) & 0xFFFFFFFF) / 4294967296

def generate_simulated_stock_data(ticker, forecast_days_int):
    known_ticker = next((t for t in POPULAR_TICKERS_PY if t["symbol"].upper() == ticker.upper()), None)
    if not known_ticker and random.random() < 0.2: # 20% chance of error for unknown tickers
        return None, f"Invalid ticker symbol: {ticker} or no data found. Please try a known ticker."

    historical_data = []
    full_forecast_data = []
    main_chart_data = []
    backtest_chart_data = []

    today = datetime.today()
    current_date = today - timedelta(days=365)

    last_price = pseudo_random_py(ticker, 1) * 300 + 50
    for i in range(365):
        date_str = format_date_py(current_date)
        change = (pseudo_random_py(ticker, i + 100) - 0.49) * (last_price * 0.05)
        last_price += change
        last_price = max(last_price, 1)
        actual_price = round(last_price, 2)
        
        historical_data.append({"ds": date_str, "y": actual_price})
        main_chart_data.append({"ds": date_str, "actual": actual_price})
        current_date += timedelta(days=1)

    historical_forecast_seed = 2000
    for i, point in enumerate(historical_data):
        forecast_noise = (pseudo_random_py(ticker, i + historical_forecast_seed) - 0.5) * (point["y"] * 0.05)
        yhat = round(point["y"] + forecast_noise, 2)
        yhat_lower = round(yhat * (1 - (0.03 + pseudo_random_py(ticker, i + historical_forecast_seed + 1) * 0.05)), 2)
        yhat_upper = round(yhat * (1 + (0.03 + pseudo_random_py(ticker, i + historical_forecast_seed + 2) * 0.05)), 2)
        full_forecast_data.append({"ds": point["ds"], "yhat": yhat, "yhat_lower": yhat_lower, "yhat_upper": yhat_upper})

    last_forecast_price = historical_data[-1]["y"]
    future_forecast_seed = 3000
    future_forecast_table_data = []
    
    current_date_forecast = today + timedelta(days=1)
    for i in range(forecast_days_int):
        date_str = format_date_py(current_date_forecast)
        trend_factor = (pseudo_random_py(ticker, i + future_forecast_seed) - 0.48) * (last_forecast_price * 0.03)
        last_forecast_price += trend_factor
        last_forecast_price = max(last_forecast_price, 1)
        
        yhat = round(last_forecast_price, 2)
        bound_percentage = 0.05 + pseudo_random_py(ticker, i + future_forecast_seed + 1) * 0.10
        yhat_lower = round(yhat * (1 - bound_percentage), 2)
        yhat_upper = round(yhat * (1 + bound_percentage), 2)

        full_forecast_data.append({"ds": date_str, "yhat": yhat, "yhat_lower": yhat_lower, "yhat_upper": yhat_upper})
        future_forecast_table_data.append({"ds": date_str, "yhat": yhat})
        main_chart_data.append({
            "ds": date_str, 
            "forecast": yhat, 
            "lowerBound": yhat_lower, 
            "upperBound": yhat_upper
        })
        current_date_forecast += timedelta(days=1)

    historical_data_for_backtest = historical_data[-7:]
    for hist_point in historical_data_for_backtest:
        corresponding_forecast = next((f for f in full_forecast_data if f["ds"] == hist_point["ds"]), None)
        if corresponding_forecast:
            backtest_chart_data.append({
                "ds": hist_point["ds"],
                "actual": hist_point["y"],
                "predicted": corresponding_forecast["yhat"]
            })

    for mc_point in main_chart_data:
        if mc_point.get("actual") is not None and mc_point.get("forecast") is None:
            ff_point = next((ff for ff in full_forecast_data if ff["ds"] == mc_point["ds"]), None)
            if ff_point:
                mc_point["forecast"] = ff_point["yhat"]
                mc_point["lowerBound"] = ff_point["yhat_lower"]
                mc_point["upperBound"] = ff_point["yhat_upper"]
    
    predicted_price_for_last_day = future_forecast_table_data[-1]["yhat"] if future_forecast_table_data else 0

    advice = InvestmentAdvice.HOLD
    if historical_data and future_forecast_table_data:
        last_actual = historical_data[-1]["y"]
        
        avg_next_few_days_forecast_sum = sum(item["yhat"] for item in future_forecast_table_data[:min(7, len(future_forecast_table_data))])
        avg_next_few_days_forecast_len = min(7, len(future_forecast_table_data))
        avg_next_few_days_forecast = avg_next_few_days_forecast_sum / avg_next_few_days_forecast_len if avg_next_few_days_forecast_len > 0 else last_actual

        overall_change = (avg_next_few_days_forecast - last_actual) / last_actual if last_actual != 0 else 0

        if overall_change > 0.03:
            advice = InvestmentAdvice.BUY
        elif overall_change < -0.03:
            advice = InvestmentAdvice.SELL

    return {
        "ticker": ticker,
        "forecastDays": forecast_days_int,
        "historicalData": historical_data,
        "fullForecastData": full_forecast_data,
        "futureForecastTableData": future_forecast_table_data,
        "predictedPriceForLastDay": predicted_price_for_last_day,
        "advice": advice,
        "backtestChartData": backtest_chart_data,
        "mainChartData": main_chart_data
    }, None


app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route('/api/predict', methods=['GET'])
def predict():
    ticker = request.args.get('ticker')
    days_str = request.args.get('days')

    if not ticker or not days_str:
        return jsonify({"error": "Missing ticker or days parameter"}), 400
    
    try:
        forecast_days_int = int(days_str)
        if forecast_days_int <= 0:
             return jsonify({"error": "Forecast days must be a positive integer"}), 400
    except ValueError:
        return jsonify({"error": "Invalid days parameter, must be an integer"}), 400

    prediction_result, error_message = generate_simulated_stock_data(ticker, forecast_days_int)

    if error_message:
         # For a 404-like error based on ticker
        if "Invalid ticker symbol" in error_message:
             return jsonify({"error": error_message}), 404
        return jsonify({"error": error_message}), 500 # Generic server error for other issues

    return jsonify(prediction_result)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    # This serves the main index.html for any route not caught by API or static files
    # React Router will then handle client-side routing.
    # If a specific file exists in static (like an image), it will be served by static_folder config.
    # However, for SPA, we always want to serve index.html for non-API, non-explicit-static routes.
    if path != "" and path.startswith('api/'): # Don't serve index.html for API routes
        return jsonify({"error": "Not found"}), 404
    
    # Check if the path points to an existing static file (e.g. manifest.json, images)
    # This is implicitly handled by Flask's static_folder serving if the file exists.
    # If it does not exist, or it's the root path, serve index.html for the SPA.
    # For a robust SPA setup, you often want to explicitly serve index.html.
    
    # A common pattern is: if path exists in static, serve it, else serve index.html
    # However, since we defined static_url_path='/static', flask handles /static/filename.ext requests.
    # For root and other non-static, non-api paths, we serve index.html.
    return send_from_directory(app.static_folder, 'index.html')


import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

