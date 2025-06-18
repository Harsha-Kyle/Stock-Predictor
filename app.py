import yfinance as yf
from prophet import Prophet
import pandas as pd
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from datetime import datetime

# Initialize app with Bootstrap
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

# Available stock options
stock_options = {
    "GOOGL - Alphabet Inc. (Google)": "GOOGL",
    "AAPL - Apple Inc.": "AAPL",
    "MSFT - Microsoft Corp.": "MSFT",
    "AMZN - Amazon.com Inc.": "AMZN",
    "TSLA - Tesla Inc.": "TSLA",
}

# Layout
app.layout = dbc.Container([
    html.Br(),

    dbc.Row([
        dbc.Col(html.H2("📈 Stock Predictor"), width="auto")
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            html.Label("Stock Ticker Symbol"),
            dcc.Dropdown(
                id="ticker-dropdown",
                options=[{"label": k, "value": v} for k, v in stock_options.items()],
                placeholder="Select a stock",
                value="GOOGL"
            ),
        ])
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            html.Label("Forecast Period (Days)"),
            dcc.Dropdown(
                id="forecast-dropdown",
                options=[{"label": f"{d} Days", "value": d} for d in [7, 15, 30, 60, 90]],
                value=15
            ),
        ])
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.Button("Predict Stock Price", id="predict-button", color="primary", block=True),
        ])
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-output",
                type="circle",
                children=html.Div(id="output-message")
            )
        ])
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id="historical-graph")
        ])
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id="forecast-graph")
        ])
    ]),

    html.Hr(),

    html.Footer([
        html.P("© 2025 Stock Predictor. All rights reserved.", style={"fontSize": "0.9rem"}),
        html.P("Disclaimer: Predictions are for informational purposes only and not financial advice.",
               style={"fontSize": "0.8rem", "color": "gray"})
    ], style={"textAlign": "center", "marginTop": "20px"}),

], fluid=True)


# Callbacks
@app.callback(
    [Output("historical-graph", "figure"),
     Output("forecast-graph", "figure"),
     Output("output-message", "children")],
    [Input("predict-button", "n_clicks")],
    [State("ticker-dropdown", "value"),
     State("forecast-dropdown", "value")]
)
def update_graphs(n_clicks, ticker, period):
    if not ticker or not period:
        return {}, {}, dbc.Alert("Please select a stock and forecast period.", color="warning")

    try:
        df = yf.download(ticker, period="2y")
        df.reset_index(inplace=True)

        # Plot Historical Prices
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Scatter(x=df["Date"], y=df["Close"],
                                      mode="lines", name="Close Price"))
        fig_hist.update_layout(title="Historical Stock Prices", template="plotly_white")

        # Prophet Forecast
        prophet_df = df[["Date", "Close"]].rename(columns={"Date": "ds", "Close": "y"})
        model = Prophet()
        model.fit(prophet_df)

        future = model.make_future_dataframe(periods=period)
        forecast = model.predict(future)

        # Plot Forecast
        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat"],
                                          mode="lines", name="Predicted"))
        fig_forecast.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat_upper"],
                                          mode="lines", name="Upper CI", line=dict(dash="dot")))
        fig_forecast.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat_lower"],
                                          mode="lines", name="Lower CI", line=dict(dash="dot")))
        fig_forecast.update_layout(title="Forecasted Stock Prices", template="plotly_white")

        return fig_hist, fig_forecast, dbc.Alert("Prediction successful!", color="success")

    except Exception as e:
        return {}, {}, dbc.Alert(f"Error: {str(e)}", color="danger")


# Run app
if __name__ == "__main__":
    app.run_server(debug=True)
