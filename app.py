import yfinance as yf
import ollama

def get_stock_data(symbol):
    print(f"Fetching data for {symbol}...")
    stock = yf.Ticker(f"{symbol}.NS")
    info = stock.info
    
    return {
        "name": info.get('longName', symbol),
        "current_price": info.get('currentPrice', 'N/A'),
        "pe_ratio": info.get('trailingPE', 'N/A'),
        "roe": info.get('returnOnEquity', 'N/A'),
        "debt_to_equity": info.get('debtToEquity', 'N/A'),
        "market_cap": info.get('marketCap', 'N/A'),
        "52_week_high": info.get('fiftyTwoWeekHigh', 'N/A'),
        "52_week_low": info.get('fiftyTwoWeekLow', 'N/A'),
        "revenue": info.get('totalRevenue', 'N/A'),
        "profit_margin": info.get('profitMargins', 'N/A')
    }

def analyze_with_ollama(data):
    print("Analyzing with Ollama...")
    
    prompt = f"""
    You are an expert Indian stock market analyst.
    Analyze this NSE stock and give a detailed report:
    
    Company: {data['name']}
    Current Price: ₹{data['current_price']}
    PE Ratio: {data['pe_ratio']}
    ROE: {data['roe']}
    Debt to Equity: {data['debt_to_equity']}
    Market Cap: {data['market_cap']}
    52 Week High: ₹{data['52_week_high']}
    52 Week Low: ₹{data['52_week_low']}
    Total Revenue: {data['revenue']}
    Profit Margin: {data['profit_margin']}
    
    Please analyze:
    1. Is this stock fundamentally strong?
    2. Is current price attractive?
    3. What are key risks?
    4. What are key opportunities?
    5. Final verdict: BUY / WATCH / AVOID
    """
    
    response = ollama.chat(
        model="llama3.1",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response['message']['content']

# ----------------------------------------
# RUN
# ----------------------------------------
symbol = input("Enter NSE stock symbol: ").upper()

data = get_stock_data(symbol)
analysis = analyze_with_ollama(data)

print("\n========== STOCK ANALYSIS ==========")
print(analysis)
print("=====================================")