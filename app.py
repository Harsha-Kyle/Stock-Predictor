import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objs as go
import yfinance as yf
from prophet import Prophet
import pandas as pd
import datetime

# Dash App
app = dash.Dash(__name__, title="Stock Predictor", update_title=None)
server = app.server

# App Layout
app.layout = html.Div(style={'backgroundColor': '#f9f9f9', 'fontFamily': 'Arial'}, children=[
    html.Div(style={'backgroundColor': '#0f172a', 'padding': '1rem'}, children=[
        html.H1("📈 Stock Predictor", style={'color': 'white', 'margin': '0'})
    ]),
    
    html.Div(style={'maxWidth': '900px', 'margin': '2rem auto', 'padding': '2rem', 'backgroundColor': '#1e293b', 'borderRadius': '1rem'}, children=[
        html.Label("Stock Ticker Symbol", style={'color': 'white'}),
        dcc.Input(id="ticker", type="text", placeholder="e.g., AAPL, RELIANCE.NS", style={'width': '100%', 'padding': '10px', 'marginTop': '10px'}),
        
        html.Br(), html.Br(),
        html.Label("Forecast Period (Days)", style={'color': 'white'}),
        dcc.Dropdown(
            id="days",
            options=[{'label': f'{i} Days', 'value': i} for i in [7, 14, 30, 60]],
            value=7,
            style={'marginTop': '10px'}
        ),
        
        html.Br(),
        html.Button("Predict Stock Price", id="predict-btn", n_clicks=0, style={'width': '100%', 'padding': '1rem', 'backgroundColor': '#334155', 'color': 'white', 'border': 'none', 'borderRadius': '0.5rem'}),
        
        html.Br(), html.Br(),
        html.Div(id="prediction-output"),
        dcc.Graph(id="forecast-graph")
    ])
])

# Callback
@app.callback(
    [Output("prediction-output", "children"),
     Output("forecast-graph", "figure")],
    [Input("predict-btn", "n_clicks")],
    [State("ticker", "value"),
     State("days", "value")]
)
def predict_stock(n_clicks, ticker, days):
    if not ticker or not days:
        return html.Div("Enter valid inputs", style={'color': 'red'}), go.Figure()

    # Fetch data
    end = datetime.date.today()
    start = end - datetime.timedelta(days=365)
    df = yf.download(ticker, start=start, end=end)

    if df.empty:
        return html.Div("Invalid ticker or no data available.", style={'color': 'red'}), go.Figure()

    df = df.reset_index()[['Date', 'Close']]
    df.rename(columns={'Date': 'ds', 'Close': 'y'}, inplace=True)

    # Prophet forecast
    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)

    # Merge for display
    merged = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    merged['Actual'] = df.set_index('ds')['y'].reindex(merged['ds']).values

    # Predicted price
    pred_price = round(merged.iloc[-1]['yhat'], 2)
    invest_suggestion = "BUY 📈" if pred_price > df['y'].iloc[-1] else "SELL 📉" if pred_price < df['y'].iloc[-1] else "HOLD ⚖️"

    # Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merged['ds'], y=merged['Actual'], mode='lines', name='Actual Price'))
    fig.add_trace(go.Scatter(x=merged['ds'], y=merged['yhat'], mode='lines', name='Forecasted Price'))
    fig.add_trace(go.Scatter(x=merged['ds'], y=merged['yhat_upper'], mode='lines', name='Upper Bound', line=dict(dash='dot'), opacity=0.3))
    fig.add_trace(go.Scatter(x=merged['ds'], y=merged['yhat_lower'], mode='lines', name='Lower Bound', line=dict(dash='dot'), opacity=0.3))

    fig.update_layout(
        plot_bgcolor='#1e293b',
        paper_bgcolor='#1e293b',
        font=dict(color='white'),
        xaxis_title="Date",
        yaxis_title="Price",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    output = html.Div([
        html.H3(f"📊 Predicted Price: ₹{pred_price}", style={'color': '#10b981'}),
        html.H4(f"📌 Suggestion: {invest_suggestion}", style={'color': '#e2e8f0'})
    ])

    return output, fig


if __name__ == '__main__':
    app.run_server(debug=True)
