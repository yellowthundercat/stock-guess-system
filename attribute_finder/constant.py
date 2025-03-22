# World bank indicator # annual
VIET_NAM_ID = 'VNM'
USA_ID = 'USA'
CHINA_ID = 'CHN'
GDP_GROWTH = 'NY.GDP.MKTP.KD.ZG'
REAL_INTEREST_RATE = 'FR.INR.RINR'
UNEMPLOYMENT_RATE = 'SL.UEM.TOTL.ZS'
INFLATION = 'FP.CPI.TOTL.ZG'
CURRENT_ACCOUNT_BALANCE = 'BN.CAB.XOKA.CD'
GOVERNMENT_DEBT = 'GC.DOD.TOTL.GD.ZS'

# Yahoo finance
BRENT_OIL = 'BZ=F'
GOLD = 'GC=F'
VIX = '^VIX'
SP500 = '^GSPC'
DOWJONES = '^DJI'
SHANGHAI = '000001.SS'
HANGSENG = '^HSI'
NIKKEI = '^N225'
KOSPI = '^KS11'
DXY = 'DX-Y.NYB'
BTC = 'BTC-USD'
ETH = 'ETH-USD'

# vnstock 
VNINDEX = 'VNINDEX'
USDVND = 'USDVND'
CNYVND = 'CNYVND'

TRADING_URL = 'https://trading.vietcap.com.vn/api/'
CHART_URL = 'chart/OHLCChart/gap'

# simplize
CHUNK_SIZE = 50

LOAD_TIME_DATA_CHUNK_SIZE = 100

# standardize
DATE = 'Date'
OPEN = 'Open'
HIGH = 'High'
LOW = 'Low'
CLOSE = 'Close'
VOLUME = 'Volume'

# ta
SMA_50 = 'SMA_50'
SMA_200 = 'SMA_200'
BBL = 'BBL_20_2.0'
BBM = 'BBM_20_2.0'
BBU = 'BBU_20_2.0'
BBB = 'BBB_20_2.0'
BBP = 'BBP_20_2.0'
RSI = 'RSI_14'
VOL_SMA_20 = 'SMA_20'
STOCHK = 'STOCHk_14_3_3'
STOCHD = 'STOCHd_14_3_3'

# Preprocess
DAY_SIZE = 29
MONTH_SIZE = 13
QUARTER_SIZE = 46 
FLAT_SIZE = 20

DEFAULT_HEADERS = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Accept-Language': 'vi',
            'Cache-Control': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'DNT': '1',
            'Pragma': 'no-cache',
        }

HEADERS_MAPPING_SOURCE =    {
        'SSI': {'Referer': 'https://iboard.ssi.com.vn', 'Origin': 'https://iboard.ssi.com.vn'},
        'VND': {'Referer': 'https://dchart.vndirect.com.vn', 'Origin': 'https://dchart.vndirect.com.vn'},
        'TCBS': {'Referer': 'https://tcinvest.tcbs.com.vn/', 'Origin': 'https://tcinvest.tcbs.com.vn/'},
        'VCI': {'Referer': 'https://trading.vietcap.com.vn/', 'Origin': 'https://trading.vietcap.com.vn/'},
        'MSN': {'Referer': 'https://www.msn.com/', 'Origin': 'https://www.msn.com/'},
        'FMARKET': {'Referer': 'https://fmarket.vn/', 'Origin': 'https://fmarket.vn/'},
    }

OHLC_MAP = {
    't': 'time',
    'o': 'open',
    'h': 'high',
    'l': 'low',
    'c': 'close',
    'v': 'volume',
}

RESAMPLE_MAP = {
            '5m' : '5min',
            '15m' : '15min',
            '30m' : '30min',
            '1W' : '1W',
            '1M' : 'M'
            }

OHLC_DTYPE = {
    "time": "datetime64[ns]",  # Convert timestamps to datetime
    "open": "float64",
    "high": "float64",
    "low": "float64",
    "close": "float64",
    "volume": "int64",
}

INTERVAL_MAP = {'1m' : 'ONE_MINUTE',
            '5m' : 'ONE_MINUTE',
            '15m' : 'ONE_MINUTE',
            '30m' : 'ONE_MINUTE',
            '1H' : 'ONE_HOUR',
            '1D' : 'ONE_DAY',
            '1W' : 'ONE_DAY',
            '1M' : 'ONE_DAY'
            }