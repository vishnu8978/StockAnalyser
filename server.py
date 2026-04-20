from flask import Flask, render_template, request, jsonify, session
import yfinance as yf
from groq import Groq
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import pytz
import pandas as pd
import io

load_dotenv()

app = Flask(__name__)
app.secret_key = "stockanalyzer2024"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com",
}

BSE_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.bseindia.com",
}

# Master stock databases
NSE_STOCKS = {}
BSE_STOCKS = {}

# Fallback dictionary for common stocks
BSE_CODES = {
    "reliance": "RELIANCE",
    "tata power": "TATAPOWER",
    "tatapower": "TATAPOWER",
    "infosys": "INFY",
    "infy": "INFY",
    "hdfc bank": "HDFCBANK",
    "hdfcbank": "HDFCBANK",
    "tcs": "TCS",
    "tata consultancy": "TCS",
    "tata consultancy services": "TCS",
    "wipro": "WIPRO",
    "icici bank": "ICICIBANK",
    "icicibank": "ICICIBANK",
    "bharti airtel": "BHARTIARTL",
    "airtel": "BHARTIARTL",
    "itc": "ITC",
    "larsen": "LT",
    "l&t": "LT",
    "asian paints": "ASIANPAINT",
    "bajaj finance": "BAJFINANCE",
    "kotak": "KOTAKBANK",
    "kotak mahindra": "KOTAKBANK",
    "zomato": "ZOMATO",
    "titan": "TITAN",
    "ultratech": "ULTRACEMCO",
    "nestle": "NESTLEIND",
    "maruti": "MARUTI",
    "maruti suzuki": "MARUTI",
    "sun pharma": "SUNPHARMA",
    "sunpharma": "SUNPHARMA",
    "adani ports": "ADANIPORTS",
    "ongc": "ONGC",
    "ntpc": "NTPC",
    "power grid": "POWERGRID",
    "sbi": "SBIN",
    "state bank": "SBIN",
    "axis bank": "AXISBANK",
    "bajaj auto": "BAJAJ-AUTO",
    "hero motocorp": "HEROMOTOCO",
    "hindalco": "HINDALCO",
    "jsw steel": "JSWSTEEL",
    "tata steel": "TATASTEEL",
    "tata motors": "TATAMOTORS",
    "dr reddy": "DRREDDY",
    "cipla": "CIPLA",
    "hcl tech": "HCLTECH",
    "hcltech": "HCLTECH",
    "tech mahindra": "TECHM",
    "techm": "TECHM",
    "mahindra": "M&M",
    "m&m": "M&M",
    "britannia": "BRITANNIA",
    "eicher motors": "EICHERMOT",
    "havells": "HAVELLS",
    "pidilite": "PIDILITIND",
    "divis lab": "DIVISLAB",
    "indusind bank": "INDUSINDBK",
    "indusind": "INDUSINDBK",
    "grasim": "GRASIM",
    "shree cement": "SHREECEM",
    "upl": "UPL",
    "coal india": "COALINDIA",
    "hindustan unilever": "HINDUNILVR",
    "hul": "HINDUNILVR",
    "paytm": "PAYTM",
    "nykaa": "NYKAA",
    "delhivery": "DELHIVERY",
    "irfc": "IRFC",
    "irctc": "IRCTC",
    "bel": "BEL",
    "bhel": "BHEL",
    "abb": "ABB",
    "siemens": "SIEMENS",
    "adani green": "ADANIGREEN",
    "adani enterprises": "ADANIENT",
    "trent": "TRENT",
    "dmart": "DMART",
    "avenue supermarts": "DMART",
    "mrf": "MRF",
    "apollo hospitals": "APOLLOHOSP",
    "persistent": "PERSISTENT",
    "mphasis": "MPHASIS",
    "coforge": "COFORGE",
    "tata elxsi": "TATAELXSI",
    "tataelxsi": "TATAELXSI",
    "ltimindtree": "LTIM",
    "yes bank": "YESBANK",
    "yesbank": "YESBANK",
    "pnb": "PNB",
    "punjab national bank": "PNB",
    "bank of baroda": "BANKBARODA",
    "canara bank": "CANBK",
    "union bank": "UNIONBANK",
    "bandhan bank": "BANDHANBNK",
    "federal bank": "FEDERALBNK",
    "idfc first": "IDFCFIRSTB",
    "idfc": "IDFCFIRSTB",
    "rbl bank": "RBLBANK",
    "au small finance": "AUBANK",
    "aubank": "AUBANK",
    "ujjivan": "UJJIVANSFB",
    "equitas": "EQUITASBNK",
    "voltas": "VOLTAS",
    "godrej consumer": "GODREJCP",
    "godrej properties": "GODREJPROP",
    "dlf": "DLF",
    "oberoi realty": "OBEROIRLTY",
    "prestige": "PRESTIGE",
    "phoenix mills": "PHOENIXLTD",
    "zydus": "ZYDUSLIFE",
    "torrent pharma": "TORNTPHARM",
    "lupin": "LUPIN",
    "biocon": "BIOCON",
    "abbott india": "ABBOTINDIA",
    "pfizer": "PFIZER",
    "page industries": "PAGEIND",
    "bata": "BATAIND",
    "relaxo": "RELAXO",
    "rajesh exports": "RAJESHEXPO",
    "tata consumer": "TATACONSUM",
    "marico": "MARICO",
    "dabur": "DABUR",
    "colgate": "COLPAL",
    "emami": "EMAMILTD",
    "godrej industries": "GODREJIND",
    "berger paints": "BERGEPAINT",
    "kansai nerolac": "KANSAINER",
    "supreme industries": "SUPREMEIND",
    "astral": "ASTRAL",
    "finolex": "FNXCABLES",
    "polycab": "POLYCAB",
    "havells india": "HAVELLS",
    "amber enterprises": "AMBER",
    "dixon technologies": "DIXON",
    "kaynes technology": "KAYNES",
    "syrma sgs": "SYRMA",
    "inox wind": "INOXWIND",
    "suzlon": "SUZLON",
    "torrent power": "TORNTPOWER",
    "cesc": "CESC",
    "jsw energy": "JSWENERGY",
    "renew power": "RNW",
    "aarti industries": "AARTIIND",
    "deepak nitrite": "DEEPAKNTR",
    "solar industries": "SOLARINDS",
    "pi industries": "PIIND",
    "rallis india": "RALLIS",
    "coromandel": "COROMANDEL",
    "chambal fertilizers": "CHAMBLFERT",
    "indigo": "INDIGO",
    "spicejet": "SPICEJET",
    "interglobe": "INDIGO",
    "container corporation": "CONCOR",
    "gateway distriparks": "GDPL",
    "blue dart": "BLUEDART",
    "mahindra logistics": "MAHLOG",
    "hdfc life": "HDFCLIFE",
    "sbi life": "SBILIFE",
    "icici lombard": "ICICIGI",
    "icici prudential": "ICICIPRULI",
    "bajaj allianz": "BAJAJFINSV",
    "star health": "STARHEALTH",
    "nuvama": "NUVAMA",
    "motilal oswal": "MOTILALOFS",
    "iifl finance": "IIFL",
    "muthoot finance": "MUTHOOTFIN",
    "manappuram": "MANAPPURAM",
    "cholamandalam": "CHOLAFIN",
    "shriram finance": "SHRIRAMFIN",
    "l&t finance": "L&TFH",
    "piramal enterprises": "PEL",
}

# ----------------------------------------
# Load NSE Stock Master List
# ----------------------------------------
def load_nse_stocks():
    global NSE_STOCKS
    try:
        print("Loading NSE stock list...")
        session_nse = requests.Session()
        session_nse.get(
            "https://www.nseindia.com",
            headers=NSE_HEADERS,
            timeout=10
        )
        url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
        response = session_nse.get(
            url, headers=NSE_HEADERS, timeout=10
        )
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            for _, row in df.iterrows():
                try:
                    symbol = str(row['SYMBOL']).strip()
                    name = str(row['NAME OF COMPANY']).strip().lower()
                    NSE_STOCKS[name] = symbol
                    NSE_STOCKS[symbol.lower()] = symbol
                except:
                    continue
            print(f"Loaded {len(NSE_STOCKS)} NSE stocks")
        else:
            print(f"NSE list failed: {response.status_code}")
    except Exception as e:
        print(f"NSE stock list error: {e}")

# ----------------------------------------
# Load BSE Stock Master List
# ----------------------------------------
def load_bse_stocks():
    global BSE_STOCKS
    try:
        print("Loading BSE stock list...")
        url = "https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w?Group=&Scripcode=&industry=&segment=Equity&status=Active"
        response = requests.get(
            url, headers=BSE_HEADERS, timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            scrips = data.get('Table', [])
            for scrip in scrips:
                try:
                    name = str(
                        scrip.get('Issuer_Name', '')
                    ).strip().lower()
                    code = str(
                        scrip.get('SCRIP_CD', '')
                    ).strip()
                    if name and code:
                        BSE_STOCKS[name] = code
                except:
                    continue
            print(f"Loaded {len(BSE_STOCKS)} BSE stocks")
        else:
            print(f"BSE list failed: {response.status_code}")
    except Exception as e:
        print(f"BSE stock list error: {e}")

# ----------------------------------------
# Find NSE Symbol
# ----------------------------------------
def find_nse_symbol(query):
    query = query.lower().strip()
    if query in NSE_STOCKS:
        return NSE_STOCKS[query]
    matches = []
    for name, symbol in NSE_STOCKS.items():
        if query in name or name in query:
            matches.append((len(name), symbol))
    if matches:
        matches.sort(key=lambda x: x[0])
        return matches[0][1]
    return None

# ----------------------------------------
# Find BSE Code
# ----------------------------------------
def find_bse_code(query):
    query = query.lower().strip()
    if query in BSE_STOCKS:
        return BSE_STOCKS[query]
    matches = []
    for name, code in BSE_STOCKS.items():
        if query in name or name in query:
            matches.append((len(name), code))
    if matches:
        matches.sort(key=lambda x: x[0])
        return matches[0][1]
    return None

# ----------------------------------------
# Helper — Get Price
# ----------------------------------------
def get_price(stock, info):
    try:
        if info:
            price = info.get('currentPrice') or \
                    info.get('regularMarketPrice')
            if price:
                return price
        try:
            fast = stock.fast_info
            price = getattr(fast, 'last_price', None)
            if price and price > 0:
                return price
        except:
            pass
        try:
            hist = stock.history(period='1d')
            if not hist.empty:
                return round(float(hist['Close'].iloc[-1]), 2)
        except:
            pass
        return None
    except:
        return None

# ----------------------------------------
# Helper — Get Week High/Low
# ----------------------------------------
def get_week_range(stock, info):
    try:
        high = info.get('fiftyTwoWeekHigh') if info else None
        low = info.get('fiftyTwoWeekLow') if info else None
        if not high or not low:
            try:
                fast = stock.fast_info
                high = high or getattr(fast, 'year_high', None)
                low = low or getattr(fast, 'year_low', None)
            except:
                pass
        return high or 'N/A', low or 'N/A'
    except:
        return 'N/A', 'N/A'

# ----------------------------------------
# Helper — Parse Financials
# ----------------------------------------
def parse_financials(stock):
    revenue_history = {}
    profit_history = {}
    try:
        financials = stock.financials
        if financials is None or financials.empty:
            return revenue_history, profit_history

        profit_row = None
        for name in [
            'Net Income',
            'Net Income Common Stockholders',
            'Net Income Continuous Operations',
            'Net Income From Continuing Operation Net Minority Interest',
            'Net Income Including Noncontrolling Interests'
        ]:
            if name in financials.index:
                profit_row = name
                break

        for col in financials.columns:
            try:
                year = str(col.year)
                if 'Total Revenue' in financials.index:
                    rev = financials.loc['Total Revenue', col]
                    if rev and str(rev) != 'nan':
                        revenue_history[year] = round(
                            float(rev)/10000000, 2
                        )
                if profit_row:
                    profit = financials.loc[profit_row, col]
                    if profit and str(profit) != 'nan':
                        profit_history[year] = round(
                            float(profit)/10000000, 2
                        )
            except:
                continue
    except Exception as e:
        print(f"Financials error: {e}")
    return revenue_history, profit_history

# ----------------------------------------
# Market Open Check
# ----------------------------------------
def is_market_open():
    try:
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        if now.weekday() >= 5:
            return False
        market_open = now.replace(hour=9, minute=15, second=0)
        market_close = now.replace(hour=15, minute=30, second=0)
        return market_open <= now <= market_close
    except:
        return False

# ----------------------------------------
# Get Indices Data
# ----------------------------------------
def get_indices_data():
    try:
        result = []

        # Source 1: Try NSE API
        try:
            session_nse = requests.Session()
            session_nse.get(
                "https://www.nseindia.com",
                headers=NSE_HEADERS, timeout=3
            )
            response = session_nse.get(
                "https://www.nseindia.com/api/allIndices",
                headers=NSE_HEADERS, timeout=3
            )

            if response.status_code == 200:
                data = response.json()
                wanted = [
                    'NIFTY 50', 'NIFTY BANK',
                    'NIFTY MIDCAP 100',
                    'NIFTY SMLCAP 100',
                    'INDIA VIX'
                ]
                for index in data.get('data', []):
                    name = index.get('index', '')
                    if name in wanted:
                        change = index.get('percentChange', 0)
                        result.append({
                            "name": name,
                            "price": index.get('last', 0),
                            "percent_change": change,
                            "direction": "up" if float(
                                change or 0
                            ) >= 0 else "down"
                        })
        except Exception as e:
            print(f"NSE API error: {e}")

        # Source 2: yfinance for indices
        # Use if NSE API fails or to supplement
        yf_indices = {
            "NIFTY 50": "^NSEI",
            "SENSEX": "^BSESN",
            "NIFTY BANK": "^NSEBANK",
            "INDIA VIX": "^INDIAVIX",
        }

        fetched_names = [r['name'] for r in result]

        for name, ticker in yf_indices.items():
            try:
                if name not in fetched_names:
                    stock = yf.Ticker(ticker)
                    fast = stock.fast_info
                    price = getattr(fast, 'last_price', None)
                    prev = getattr(fast, 'previous_close', None)

                    if price and prev:
                        change = round(
                            ((price - prev) / prev * 100), 2
                        )
                        result.append({
                            "name": name,
                            "price": round(price, 2),
                            "percent_change": change,
                            "direction": "up" if change >= 0 else "down"
                        })
            except Exception as e:
                print(f"yfinance index error {name}: {e}")

        # Always add Sensex
        try:
            sensex_in = any(r['name'] == 'SENSEX' for r in result)
            if not sensex_in:
                stock = yf.Ticker("^BSESN")
                fast = stock.fast_info
                price = getattr(fast, 'last_price', None)
                prev = getattr(fast, 'previous_close', None)
                if price and prev:
                    change = round(((price - prev) / prev * 100), 2)
                    result.insert(2, {
                        "name": "SENSEX",
                        "price": round(price, 2),
                        "percent_change": change,
                        "direction": "up" if change >= 0 else "down"
                    })
        except Exception as e:
            print(f"Sensex error: {e}")

        # Sort in correct order
        order = [
            'NIFTY 50', 'NIFTY BANK', 'SENSEX',
            'NIFTY MIDCAP 100', 'NIFTY SMLCAP 100', 'INDIA VIX'
        ]
        result.sort(
            key=lambda x: order.index(x['name'])
            if x['name'] in order else 99
        )

        return {
            "indices": result,
            "market_open": is_market_open(),
            "timestamp": datetime.now(
                pytz.timezone('Asia/Kolkata')
            ).strftime("%d %b %Y %I:%M:%S %p IST")
        }

    except Exception as e:
        print(f"Indices error: {e}")
        return {"indices": [], "market_open": False}
# ----------------------------------------
# Get NSE Market Data
# ----------------------------------------
def get_nse_market_data(symbol):
    try:
        session_nse = requests.Session()
        session_nse.get(
            "https://www.nseindia.com",
            headers=NSE_HEADERS, timeout=5
        )
        response = session_nse.get(
            f"https://www.nseindia.com/api/quote-equity?symbol={symbol}",
            headers=NSE_HEADERS, timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            trade = data.get('tradeInfo', {})
            price = data.get('priceInfo', {})
            info = data.get('info', {})
            return {
                "nse_vwap": price.get('vwap', 'N/A'),
                "nse_lower_circuit": price.get('lowerCP', 'N/A'),
                "nse_upper_circuit": price.get('upperCP', 'N/A'),
                "delivery_percent": trade.get(
                    'deliveryToTradedQuantity', 'N/A'
                ),
                "total_traded_volume": trade.get(
                    'totalTradedVolume', 'N/A'
                ),
                "face_value": info.get('faceValue', 'N/A'),
            }
        return {}
    except Exception as e:
        print(f"NSE market data error: {e}")
        return {}

# ----------------------------------------
# Fetch Stock Data Helper
# ----------------------------------------
def fetch_stock(symbol, suffixes=['.NS', '.BO', '']):
    for suffix in suffixes:
        try:
            ticker = f"{symbol}{suffix}"
            stock = yf.Ticker(ticker)
            info = stock.info
            price = get_price(stock, info)
            if price:
                print(f"Found: {ticker} = {price}")
                return stock, info, price
        except Exception as e:
            print(f"Failed {symbol}{suffix}: {e}")
            continue
    return None, None, None

# ----------------------------------------
# Get NSE Stock Data
# ----------------------------------------
def get_nse_stock_data(symbol):
    try:
        # Try NSE master list first
        found = find_nse_symbol(symbol)
        if found:
            symbol = found
            print(f"NSE master list found: {symbol}")

        stock, info, price = fetch_stock(symbol)

        if not price:
            return {"error": f"'{symbol}' not found. Please check the symbol."}

        week_high, week_low = get_week_range(stock, info)
        revenue_history, profit_history = parse_financials(stock)
        nse_extra = get_nse_market_data(symbol)

        return {
            "name": info.get('longName', symbol) if info else symbol,
            "symbol": symbol,
            "current_price": price,
            "pe_ratio": round(info.get('trailingPE', 0) or 0, 2) if info else 0,
            "roe": round((info.get('returnOnEquity', 0) or 0) * 100, 2) if info else 0,
            "debt_to_equity": round(info.get('debtToEquity', 0) or 0, 2) if info else 0,
            "market_cap": info.get('marketCap', 'N/A') if info else 'N/A',
            "week_high": week_high,
            "week_low": week_low,
            "revenue": info.get('totalRevenue', 'N/A') if info else 'N/A',
            "profit_margin": round((info.get('profitMargins', 0) or 0) * 100, 2) if info else 0,
            "dividend_yield": round((info.get('dividendYield', 0) or 0) * 100, 2) if info else 0,
            "volume": info.get('averageVolume', 'N/A') if info else 'N/A',
            "revenue_history": revenue_history,
            "profit_history": profit_history,
            "sector": info.get('sector', 'N/A') if info else 'N/A',
            "industry": info.get('industry', 'N/A') if info else 'N/A',
            "exchange": "NSE",
            **nse_extra
        }

    except Exception as e:
        print(f"NSE error: {e}")
        return {"error": f"Could not fetch '{symbol}'"}

# ----------------------------------------
# Get BSE Stock Data
# ----------------------------------------
def get_bse_stock_data(company_name):
    try:
        search_key = company_name.lower().strip()
        symbol = None

        # Step 1: Check fallback dictionary
        if search_key in BSE_CODES:
            symbol = BSE_CODES[search_key]
        else:
            for key in BSE_CODES:
                if search_key in key or key in search_key:
                    symbol = BSE_CODES[key]
                    break

        # Step 2: Search NSE master list
        if not symbol:
            found = find_nse_symbol(company_name)
            if found:
                symbol = found
                print(f"NSE master list: {symbol}")

        # Step 3: Search BSE master list
        if not symbol:
            bse_numeric = find_bse_code(company_name)
            if bse_numeric:
                print(f"BSE master list: {bse_numeric}")
                stock, info, price = fetch_stock(
                    bse_numeric, ['.BO', '.NS', '']
                )
                if price:
                    week_high, week_low = get_week_range(stock, info)
                    revenue_history, profit_history = parse_financials(stock)
                    return {
                        "name": info.get('longName', company_name) if info else company_name,
                        "bse_code": bse_numeric,
                        "symbol": bse_numeric,
                        "current_price": price,
                        "pe_ratio": round(info.get('trailingPE', 0) or 0, 2) if info else 0,
                        "roe": round((info.get('returnOnEquity', 0) or 0) * 100, 2) if info else 0,
                        "debt_to_equity": round(info.get('debtToEquity', 0) or 0, 2) if info else 0,
                        "market_cap": info.get('marketCap', 'N/A') if info else 'N/A',
                        "week_high": week_high,
                        "week_low": week_low,
                        "profit_margin": round((info.get('profitMargins', 0) or 0) * 100, 2) if info else 0,
                        "dividend_yield": round((info.get('dividendYield', 0) or 0) * 100, 2) if info else 0,
                        "volume": info.get('averageVolume', 'N/A') if info else 'N/A',
                        "bse_volume": info.get('averageVolume', 'N/A') if info else 'N/A',
                        "face_value": info.get('faceValue', 'N/A') if info else 'N/A',
                        "sector": info.get('sector', 'N/A') if info else 'N/A',
                        "industry": info.get('industry', 'N/A') if info else 'N/A',
                        "revenue_history": revenue_history,
                        "profit_history": profit_history,
                        "exchange": "BSE"
                    }

        # Step 4: Try guessed symbol
        if not symbol:
            guessed = company_name.upper().strip()
            guessed = guessed.replace(' BANK', 'BANK')
            guessed = guessed.replace(' LIMITED', '')
            guessed = guessed.replace(' LTD', '')
            guessed = guessed.replace(' INDUSTRIES', '')
            guessed = guessed.replace(' INDIA', '')
            guessed = guessed.replace(' ', '')
            symbol = guessed
            print(f"Guessed symbol: {symbol}")

        # Fetch data
        stock, info, price = fetch_stock(
            symbol, ['.BO', '.NS', '']
        )

        if not price:
            return {
                "error": f"'{company_name}' not found. Try NSE tab with exact symbol."
            }

        week_high, week_low = get_week_range(stock, info)
        revenue_history, profit_history = parse_financials(stock)

        return {
            "name": info.get('longName', company_name) if info else company_name,
            "bse_code": symbol,
            "symbol": symbol,
            "current_price": price,
            "pe_ratio": round(info.get('trailingPE', 0) or 0, 2) if info else 0,
            "roe": round((info.get('returnOnEquity', 0) or 0) * 100, 2) if info else 0,
            "debt_to_equity": round(info.get('debtToEquity', 0) or 0, 2) if info else 0,
            "market_cap": info.get('marketCap', 'N/A') if info else 'N/A',
            "week_high": week_high,
            "week_low": week_low,
            "profit_margin": round((info.get('profitMargins', 0) or 0) * 100, 2) if info else 0,
            "dividend_yield": round((info.get('dividendYield', 0) or 0) * 100, 2) if info else 0,
            "volume": info.get('averageVolume', 'N/A') if info else 'N/A',
            "bse_volume": info.get('averageVolume', 'N/A') if info else 'N/A',
            "face_value": info.get('faceValue', 'N/A') if info else 'N/A',
            "sector": info.get('sector', 'N/A') if info else 'N/A',
            "industry": info.get('industry', 'N/A') if info else 'N/A',
            "revenue_history": revenue_history,
            "profit_history": profit_history,
            "exchange": "BSE"
        }

    except Exception as e:
        print(f"BSE error: {e}")
        return {"error": f"Could not find '{company_name}'. Try NSE tab."}

# ----------------------------------------
# AI Analysis
# ----------------------------------------
def get_analysis(data, exchange):
    try:
        if exchange == "NSE":
            extra = f"""
=== NSE MARKET DATA ===
VWAP: {data.get('nse_vwap', 'N/A')}
Delivery %: {data.get('delivery_percent', 'N/A')}%
Upper Circuit: {data.get('nse_upper_circuit', 'N/A')}
Lower Circuit: {data.get('nse_lower_circuit', 'N/A')}
Revenue History (Cr): {data.get('revenue_history', {})}
Profit History (Cr): {data.get('profit_history', {})}
            """
        else:
            extra = f"""
=== BSE DATA ===
BSE Code: {data.get('bse_code', 'N/A')}
Revenue History (Cr): {data.get('revenue_history', {})}
Profit History (Cr): {data.get('profit_history', {})}
            """

        prompt = f"""
You are an expert Indian stock market analyst.
Analyze this {exchange} stock:

Company: {data.get('name')}
Exchange: {exchange}
Sector: {data.get('sector', 'N/A')}
Current Price: {data.get('current_price')}
PE Ratio: {data.get('pe_ratio')}
ROE: {data.get('roe')}%
Debt to Equity: {data.get('debt_to_equity')}
Market Cap: {data.get('market_cap')}
52 Week High: {data.get('week_high')}
52 Week Low: {data.get('week_low')}
Profit Margin: {data.get('profit_margin')}%
Dividend Yield: {data.get('dividend_yield')}%
{extra}

Give analysis in exactly this format:

FUNDAMENTAL: (2-3 lines)

TECHNICAL: (2-3 lines)

MARKET SENTIMENT: (1-2 lines)

RISKS: (2-3 risks)

OPPORTUNITIES: (2-3 opportunities)

VERDICT: BUY or WATCH or AVOID

ENTRY: (single number only, example: 780)

TARGET: (single number only, example: 950)

STOPLOSS: (single number only, example: 720)

Important: For ENTRY, TARGET and STOPLOSS
write ONLY a single number.
No text, no ranges, no approximately.
Just one number like 780
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
# Chat
# ----------------------------------------
def chat_about_stock(question, stock_data, chat_history):
    try:
        system = f"""
You are an expert Indian stock market analyst.
Answer questions about this stock:

Company: {stock_data.get('name')}
Exchange: {stock_data.get('exchange', 'NSE')}
Sector: {stock_data.get('sector')}
Current Price: {stock_data.get('current_price')}
PE Ratio: {stock_data.get('pe_ratio')}
ROE: {stock_data.get('roe')}%
Debt to Equity: {stock_data.get('debt_to_equity')}
Market Cap: {stock_data.get('market_cap')}
52 Week High: {stock_data.get('week_high')}
52 Week Low: {stock_data.get('week_low')}
Profit Margin: {stock_data.get('profit_margin')}%
Dividend Yield: {stock_data.get('dividend_yield')}%
Revenue History (Cr): {stock_data.get('revenue_history', {})}
Profit History (Cr): {stock_data.get('profit_history', {})}
Delivery %: {stock_data.get('delivery_percent', 'N/A')}
VWAP: {stock_data.get('nse_vwap', 'N/A')}

Rules:
- Answer directly and concisely
- Never show calculation steps
- Just give final answer with numbers
- Maximum 3-4 lines per answer
- If data not available say so honestly
- Always relate to Indian market context
- Use rupee symbol for currency
- Express large numbers in Crores
- Be confident in analysis
        """

        messages = [{"role": "system", "content": system}]
        for msg in chat_history[-10:]:
            messages.append(msg)
        messages.append({"role": "user", "content": question})

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=500
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Chat error: {str(e)}"

# ----------------------------------------
# Routes
# ----------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/indices', methods=['GET'])
def indices():
    data = get_indices_data()
    return jsonify(data)

@app.route('/analyze', methods=['POST'])
def analyze():
    symbol = request.json.get('symbol', '').upper().strip()
    exchange = request.json.get('exchange', 'NSE')

    if not symbol:
        return jsonify({"error": "Please enter a stock symbol"})

    if exchange == 'NSE':
        data = get_nse_stock_data(symbol)
    else:
        data = get_bse_stock_data(symbol)

    if "error" in data:
        return jsonify({"error": data["error"]})

    analysis = get_analysis(data, exchange)
    session['stock_data'] = data
    session['chat_history'] = []

    return jsonify({
        "symbol": symbol,
        "exchange": exchange,
        "data": data,
        "analysis": analysis
    })

@app.route('/chat', methods=['POST'])
def chat():
    question = request.json.get('question', '').strip()
    if not question:
        return jsonify({"error": "Please type a question"})

    stock_data = session.get('stock_data')
    if not stock_data:
        return jsonify({"error": "Please analyze a stock first"})

    chat_history = session.get('chat_history', [])
    answer = chat_about_stock(question, stock_data, chat_history)

    chat_history.append({"role": "user", "content": question})
    chat_history.append({"role": "assistant", "content": answer})
    session['chat_history'] = chat_history

    return jsonify({"answer": answer})

# ----------------------------------------
# Run
# ----------------------------------------
if __name__ == '__main__':
    load_nse_stocks()
    load_bse_stocks()
    app.run(debug=True, port=8080)