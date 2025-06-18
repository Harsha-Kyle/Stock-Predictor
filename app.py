import dash
from dash import html, dcc, Input, Output, State
import yfinance as yf
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.graph_objs as go
from datetime import date, timedelta

# Initialize the app
app = dash.Dash(__name__, title="Stock Predictor", suppress_callback_exceptions=True)
server = app.server  # for Render deployment

# Ticker options (as seen in your UI)
ticker_options = [
    {'label': 'AAPL - Apple Inc.', 'value': 'AAPL'},
    {'label': 'GOOGL - Alphabet Inc. (Google)', 'value': 'GOOGL'},
    {'label': 'MSFT - Microsoft Corp.', 'value': 'MSFT'},
    {'label': 'TSLA - Tesla, Inc.', 'value': 'TSLA'},
    {'label': 'AMZN - Amazon.com, Inc.', 'value': 'AMZN'},
    {'label': 'META - Meta Platforms, Inc.', 'value': 'META'},
    {'label': 'RELIANCE.NS - Reliance Industries Ltd.', 'value': 'RELIANCE.NS'},
    {'label': 'TCS.NS - Tata Consultancy Services Ltd.', 'value': 'TCS.NS'},
    {'label': 'INFY.NS - Infosys Ltd.', 'value': 'INFY.NS'},
    {'label': 'NVDA - NVIDIA Corporation', 'value': 'NVDA'}
]

forecast_options = [
    {"label": f"{d} Days", "value": d} for d in [7, 15, 30, 60, 90]
]

app.layout = html.Div([
    html.Div([
        html.H1("📈 Stock Predictor", className="text-3xl font-bold text-white"),
    ], className="bg-gray-900 px-6 py-4 flex justify-between items-center"),

    html.Div([
        html.Div([
            html.Label("Stock Ticker Symbol", className="text-sm text-white mb-2"),
            dcc.Dropdown(
                id="ticker-input",
                options=ticker_options,
                placeholder="e.g., AAPL, RELIANCE.NS",
                className="text-black"
            ),
            html.Label("Forecast Period (Days)", className="text-sm text-white mt-4 mb-2"),
            dcc.Dropdown(
                id="forecast-days",
                options=forecast_options,
                value=7,
                className="text-black"
            ),
            html.Button("Predict Stock Price", id="predict-btn",
                        className="mt-4 bg-gray-700 text-white px-4 py-2 rounded")
        ], className="bg-gray-800 p-6 rounded shadow-md w-full max-w-xl")
    ], className="flex justify-center mt-10"),

    html.Div(id="output-section", className="mt-10 px-4"),

    html.Footer([
        html.Div([
            html.P("© 2025 Stock Predictor. All rights reserved.", className="text-sm"),
            html.P("Disclaimer: Predictions are for informational purposes only and not financial advice.", className="text-xs mt-1")
        ], className="text-center text-gray-400")
    ], className="bg-gray-900 py-4 mt-10")
], className="bg-gray-100 min-h-screen font-sans")

# Callback to run prediction
@app.callback(
    Output("output-section", "children"),
    Input("predict-btn", "n_clicks"),
    State("ticker-input", "value"),
    State("forecast-days", "value"),
)
def update_prediction(n_clicks, ticker, days):
    if not n_clicks or not ticker:
        return html.Div([
            html.Div([
                html.H2("Welcome to Stock Predictor", className="text-xl font-bold text-white mb-2"),
                html.P("Enter a stock ticker symbol and select a forecast period to get started.", className="text-white"),
                html.Img(src="https://i.imgur.com/Z4Z9Zsm.jpg", className="mt-4 rounded-lg shadow-md")
            ], className="bg-gray-800 p-6 rounded shadow-md text-center")
        ])

    # Load data
    end = date.today()
    start = end - timedelta(days=365 * 2)
    df = yf.download(ticker, start=start, end=end)

    if df.empty:
        return html.Div("No data found for the ticker!", className="text-red-500")

    df.reset_index(inplace=True)
    df = df[["Date", "Close"]].rename(columns={"Date": "ds", "Close": "y"})

    # Train Prophet
    model = Prophet()
    model.fit(df)

    # Future forecast
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)

    # Summary info
    last_price = df["y"].iloc[-1]
    predicted_price = forecast["yhat"].iloc[-1]
    investment_suggestion = "BUY 📈" if predicted_price > last_price * 1.05 else "SELL 📉" if predicted_price < last_price * 0.95 else "HOLD (Neutral)"

    # Price forecast chart
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(x=df['ds'], y=df['y'], mode='lines', name='Actual Price'))
    fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecasted Price'))
    fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], mode='lines', name='Lower Bound', line=dict(dash='dot')))
    fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], mode='lines', name='Upper Bound', line=dict(dash='dot')))
    fig_forecast.update_layout(title='Price Forecast Chart', margin=dict(l=20, r=20, t=30, b=20), height=400)

    # Backtest chart
    recent_actual = df.tail(7)
    backtest = model.predict(recent_actual[["ds"]])
    fig_backtest = go.Figure()
    fig_backtest.add_trace(go.Scatter(x=recent_actual['ds'], y=recent_actual['y'], mode='lines+markers', name='Actual Price'))
    fig_backtest.add_trace(go.Scatter(x=recent_actual['ds'], y=backtest['yhat'], mode='lines+markers', name='Predicted Price (Backtest)'))
    fig_backtest.update_layout(title='Backtest (Last 7 Days)', margin=dict(l=20, r=20, t=30, b=20), height=300)

    return html.Div([
        html.Div([
            html.H3("Prediction Summary", className="text-white text-xl mb-2"),
            html.P(f"Results for: {ticker}", className="text-green-400"),
            html.P(f"Forecast Period: {days} Days", className="text-gray-200"),
            html.Div([
                html.Div(f"₹{predicted_price:.2f}", className="text-2xl font-bold"),
                html.Small("Predicted Price (End of Period)", className="text-gray-400")
            ], className="p-4 bg-gray-700 text-white rounded mr-4"),
            html.Div([
                html.Div(investment_suggestion, className="text-2xl font-bold"),
                html.Small("Investment Suggestion", className="text-gray-400")
            ], className="p-4 bg-gray-700 text-white rounded")
        ], className="bg-gray-800 text-white p-6 rounded mb-6"),

        html.Div([
            dcc.Graph(figure=fig_forecast)
        ], className="bg-gray-800 p-6 rounded mb-6"),

        html.Div([
            html.H4("Backtest (Last 7 Days)", className="text-white mb-2"),
            dcc.Graph(figure=fig_backtest)
        ], className="bg-gray-800 p-6 rounded")
    ])

if __name__ == "__main__":
    app.run_server(debug=True)
