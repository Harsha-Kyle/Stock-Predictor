from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
from prophet import Prophet
import plotly.graph_objs as go
import json

app = Flask(__name__)

def forecast_stock(ticker, period):
    df = yf.download(ticker, period="2y")
    df.reset_index(inplace=True)
    df = df[['Date', 'Close']]
    df.rename(columns={'Date': 'ds', 'Close': 'y'}, inplace=True)

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=period)
    forecast = model.predict(future)

    last_prediction = forecast.iloc[-1]
    predicted_price = round(last_prediction['yhat'], 2)

    actual_price = df.iloc[-1]['y']
    suggestion = "BUY" if predicted_price > actual_price * 1.05 else "SELL" if predicted_price < actual_price * 0.95 else "HOLD"

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], name='Actual Price'))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Forecasted Price'))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], name='Upper Bound', line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], name='Lower Bound', line=dict(dash='dot')))
    fig.update_layout(title=f'{ticker} Forecast', xaxis_title='Date', yaxis_title='Price')

    chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return predicted_price, suggestion, chart_json

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form['ticker'].strip().upper()
        period = int(request.form['period'])

        try:
            predicted_price, suggestion, chart = forecast_stock(ticker, period)
            return render_template('index.html',
                                   ticker=ticker,
                                   period=period,
                                   predicted_price=predicted_price,
                                   suggestion=suggestion,
                                   chart=chart)
        except Exception as e:
            return render_template('index.html', error=str(e))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

