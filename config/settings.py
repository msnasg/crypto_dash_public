# config/settings.py

tabs = [
    {"name": "Home", "path": "/", "icon": "📊"},    
    {"name": "Trade Assistant", "path": "/trade-assistant", "icon": "💰"},            
    {"name": "Transactions", "path": "/transactions", "icon": "💰"},  
    {"name": "Whale Tracker", "path": "/large-transactions", "icon": "🐋"},  # "Large Transactions"
    {"name": "Futures", "path": "/futures", "icon": "📈"},         
    {"name": "Options", "path": "/options", "icon": "🚨"},        
    {"name": "On-Chain", "path": "/onchain", "icon": "🤖"},   
    {"name": "Pair Analysis", "path": "/pairanalysis", "icon": "🔗"},      
    {"name": "Sentiments", "path": "/sentiments", "icon": "📣"},  
    {"name": "ML", "path": "/machine-learning", "icon": "🧠"},  # "Machine Learning"
    {"name": "TS/Stats", "path": "/stats", "icon": "📈"},         
    {"name": "Signals", "path": "/signals", "icon": "🚨"},        
    {"name": "Portfolio", "path": "/portfolio", "icon": "💼"},    
    {"name": "Risk", "path": "/risk", "icon": "⚠️"},              
    {"name": "Auto Trade", "path": "/auto-trade", "icon": "🤖"},  
    {"name": "My Trades", "path": "/my-trade", "icon": "🧾"},     
    {"name": "Reports", "path": "/reports", "icon": "📑"},        
    {"name": "Settings", "path": "/settings", "icon": "⚙️"},      
]

default_symbols = ['BTCUSDC', 'BNBUSDC', "SOLUSDC",'ETHUSDC', 'XRPUSDC', 'DOGEUSDC', 'ADAUSDC', "HEMIUSDC", "BIOUSDC", "AVAXUSDC", "NILUSDC", "XLMUSDC",'LTCUSDC']
# ['BTCUSDT', 'DOTUSDC','XLMUSDC', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'DOGEUSDT', 'ADAUSDT']
# default_coins = ['BTC', 'BNB', 'SOL', 'ETH',  'XRP', 'DOT','XLM',  'DOGE', 'ADA']

default_coins = [
    symbol for symbol in default_symbols if not symbol.endswith('USDC')
]

