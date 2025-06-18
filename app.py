from flask import Flask, request, jsonify
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# -------- STOCK LOGIC --------

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
    {"symbol": "NVDA", "name": "NVIDIA Corporation"},
]

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
    if not known_ticker and random.random() < 0.2:
        return None, f"Invalid ticker symbol: {ticker} or no data found. Please try a known ticker."

    historical_data = []
    future_forecast_table_data = []
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
        current_date += timedelta(days=1)

    last_forecast_price = historical_data[-1]["y"]
    current_date_forecast = today + timedelta(days=1)
    future_forecast_seed = 3000

    for i in range(forecast_days_int):
        date_str = format_date_py(current_date_forecast)
        trend_factor = (pseudo_random_py(ticker, i + future_forecast_seed) - 0.48) * (last_forecast_price * 0.03)
        last_forecast_price += trend_factor
        last_forecast_price = max(last_forecast_price, 1)
        yhat = round(last_forecast_price, 2)
        future_forecast_table_data.append({"ds": date_str, "yhat": yhat})
        current_date_forecast += timedelta(days=1)

    predicted_price_for_last_day = future_forecast_table_data[-1]["yhat"] if future_forecast_table_data else 0

    advice = InvestmentAdvice.HOLD
    if historical_data and future_forecast_table_data:
        last_actual = historical_data[-1]["y"]
        avg_next = sum(item["yhat"] for item in future_forecast_table_data[:min(7, len(future_forecast_table_data))]) / min(7, len(future_forecast_table_data))
        overall_change = (avg_next - last_actual) / last_actual if last_actual != 0 else 0

        if overall_change > 0.03:
            advice = InvestmentAdvice.BUY
        elif overall_change < -0.03:
            advice = InvestmentAdvice.SELL

    return {
        "ticker": ticker,
        "forecastDays": forecast_days_int,
        "predictedPriceForLastDay": predicted_price_for_last_day,
        "advice": advice
    }, None

# -------- API + FRONTEND --------

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>Stock Forecast</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f8f9fa;
                padding: 20px;
            }
            h2 {
                color: #333;
            }
            form {
                margin-bottom: 20px;
            }
            input, button {
                padding: 8px;
                margin: 5px;
                font-size: 16px;
            }
            #result {
                background: #fff;
                padding: 15px;
                border: 1px solid #ccc;
                border-radius: 5px;
                max-width: 400px;
            }
        </style>
    </head>
    <body>
        <h2>Stock Price Predictor</h2>
        <form method="GET" action="/predict">
            <input type="text" name="ticker" placeholder="Ticker (e.g. AAPL)" required>
            <input type="number" name="days" placeholder="Forecast Days" required>
            <button type="submit">Predict</button>
        </form>
        <div id="result">
            {% if result %}
                <p><strong>Advice:</strong> {{ result['advice'] }}</p>
                <p><strong>Predicted Price:</strong> ₹{{ result['predictedPriceForLastDay'] }}</p>
            {% endif %}
        </div>
    </body>
    </html>
    '''

@app.route('/predict')
def predict():
    ticker = request.args.get('ticker')
    days = request.args.get('days')

    if not ticker or not days:
        return "<p>Missing ticker or days</p>"

    try:
        forecast_days_int = int(days)
    except ValueError:
        return "<p>Invalid number of days</p>"

    prediction_result, error = generate_simulated_stock_data(ticker, forecast_days_int)

    if error:
        return f"<p>Error: {error}</p>"

    return f'''
    <html>
    <head>
        <title>Result - {ticker.upper()}</title>
    </head>
    <body>
        <h2>Forecast Result</h2>
        <p><strong>Ticker:</strong> {ticker.upper()}</p>
        <p><strong>Forecast Days:</strong> {forecast_days_int}</p>
        <p><strong>Predicted Price:</strong> ₹{prediction_result['predictedPriceForLastDay']}</p>
        <p><strong>Advice:</strong> {prediction_result['advice']}</p>
        <a href="/">Back</a>
    </body>
    </html>
    '''

# -------- MAIN --------

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
