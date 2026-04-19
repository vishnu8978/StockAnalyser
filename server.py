from flask import Flask, render_template, request, jsonify
import yfinance as yf
from groq import Groq
import os

app = Flask(__name__)

# ----------------------------------------
# Groq Client
# ----------------------------------------
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ----------------------------------------
# Get Stock Data from yfinance
# ----------------------------------------
def get_stock_data(symbol):
    try:
        stock = yf.Ticker(f"{symbol}.NS")
        info = stock.info

        if not info or (info.get('regularMarketPrice') is None 
                        and info.get('currentPrice') is None):
            return {"error": f"Stock {symbol} not found on NSE"}

        return {
            "name": info.get('longName', symbol),
            "current_price": info.get('currentPrice') or info.get('regularMarketPrice') or 'N/A',
            "pe_ratio": round(info.get('trailingPE', 0) or 0, 2),
            "roe": round((info.get('returnOnEquity', 0) or 0) * 100, 2),
            "debt_to_equity": round(info.get('debtToEquity', 0) or 0, 2),
            "market_cap": info.get('marketCap', 'N/A'),
            "week_high": info.get('fiftyTwoWeekHigh', 'N/A'),
            "week_low": info.get('fiftyTwoWeekLow', 'N/A'),
            "revenue": info.get('totalRevenue', 'N/A'),
            "profit_margin": round((info.get('profitMargins', 0) or 0) * 100, 2),
            "dividend_yield": round((info.get('dividendYield', 0) or 0) * 100, 2),
            "volume": info.get('averageVolume', 'N/A')
        }
    except Exception as e:
        return {"error": f"Could not fetch {symbol} — please check symbol"}

# ----------------------------------------
# Analyze with Groq
# ----------------------------------------
def analyze_with_groq(symbol, data):
    try:
        prompt = f"""
        You are an expert Indian stock market analyst.
        Analyze this NSE stock and give a detailed report:

        Company: {data['name']}
        Current Price: {data['current_price']}
        PE Ratio: {data['pe_ratio']}
        ROE: {data['roe']}%
        Debt to Equity: {data['debt_to_equity']}
        Market Cap: {data['market_cap']}
        52 Week High: {data['week_high']}
        52 Week Low: {data['week_low']}
        Total Revenue: {data['revenue']}
        Profit Margin: {data['profit_margin']}%
        Dividend Yield: {data['dividend_yield']}%

        Give analysis in exactly this format:

        FUNDAMENTAL: (2-3 lines about financial health)

        TECHNICAL: (2-3 lines about price position)

        RISKS: (2-3 key risks)

        OPPORTUNITIES: (2-3 key opportunities)

        VERDICT: BUY or WATCH or AVOID

        ENTRY: (suggested entry price)

        TARGET: (price target)

        STOPLOSS: (stop loss price)
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Analysis error: {str(e)}"

# ----------------------------------------
# Routes
# ----------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    symbol = request.json.get('symbol', '').upper().strip()
    if not symbol:
        return jsonify({"error": "Please enter a stock symbol"})
    data = get_stock_data(symbol)
    if "error" in data:
        return jsonify({"error": data["error"]})
    analysis = analyze_with_groq(symbol, data)
    return jsonify({
        "symbol": symbol,
        "data": data,
        "analysis": analysis
    })

# ----------------------------------------
# Run App
# ----------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=8080)