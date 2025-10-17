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

VCI_GRAPHQL_URL = 'https://trading.vietcap.com.vn/data-mt/graphql'

VCI_REPORT_GRAPHQL = "{\"query\":\"fragment Ratios on CompanyFinancialRatio {\\n  ticker\\n  yearReport\\n  lengthReport\\n  updateDate\\n  revenue\\n  revenueGrowth\\n  netProfit\\n  netProfitGrowth\\n  ebitMargin\\n  roe\\n  roic\\n  roa\\n  pe\\n  pb\\n  eps\\n  currentRatio\\n  cashRatio\\n  quickRatio\\n  interestCoverage\\n  ae\\n  netProfitMargin\\n  grossMargin\\n  ev\\n  issueShare\\n  ps\\n  pcf\\n  bvps\\n  evPerEbitda\\n  BSA1\\n  BSA2\\n  BSA5\\n  BSA8\\n  BSA10\\n  BSA159\\n  BSA16\\n  BSA22\\n  BSA23\\n  BSA24\\n  BSA162\\n  BSA27\\n  BSA29\\n  BSA43\\n  BSA46\\n  BSA50\\n  BSA209\\n  BSA53\\n  BSA54\\n  BSA55\\n  BSA56\\n  BSA58\\n  BSA67\\n  BSA71\\n  BSA173\\n  BSA78\\n  BSA79\\n  BSA80\\n  BSA175\\n  BSA86\\n  BSA90\\n  BSA96\\n  CFA21\\n  CFA22\\n  at\\n  fat\\n  acp\\n  dso\\n  dpo\\n  ccc\\n  de\\n  le\\n  ebitda\\n  ebit\\n  dividend\\n  RTQ10\\n  charterCapitalRatio\\n  RTQ4\\n  epsTTM\\n  charterCapital\\n  fae\\n  RTQ17\\n  CFA26\\n  CFA6\\n  CFA9\\n  BSA85\\n  CFA36\\n  BSB98\\n  BSB101\\n  BSA89\\n  CFA34\\n  CFA14\\n  ISB34\\n  ISB27\\n  ISA23\\n  ISS152\\n  ISA102\\n  CFA27\\n  CFA12\\n  CFA28\\n  BSA18\\n  BSB102\\n  BSB110\\n  BSB108\\n  CFA23\\n  ISB41\\n  BSB103\\n  BSA40\\n  BSB99\\n  CFA16\\n  CFA18\\n  CFA3\\n  ISB30\\n  BSA33\\n  ISB29\\n  CFS200\\n  ISA2\\n  CFA24\\n  BSB105\\n  CFA37\\n  ISS141\\n  BSA95\\n  CFA10\\n  ISA4\\n  BSA82\\n  CFA25\\n  BSB111\\n  ISI64\\n  BSB117\\n  ISA20\\n  CFA19\\n  ISA6\\n  ISA3\\n  BSB100\\n  ISB31\\n  ISB38\\n  ISB26\\n  BSA210\\n  CFA20\\n  CFA35\\n  ISA17\\n  ISS148\\n  BSB115\\n  ISA9\\n  CFA4\\n  ISA7\\n  CFA5\\n  ISA22\\n  CFA8\\n  CFA33\\n  CFA29\\n  BSA30\\n  BSA84\\n  BSA44\\n  BSB107\\n  ISB37\\n  ISA8\\n  BSB109\\n  ISA19\\n  ISB36\\n  ISA13\\n  ISA1\\n  BSB121\\n  ISA14\\n  BSB112\\n  ISA21\\n  ISA10\\n  CFA11\\n  ISA12\\n  BSA15\\n  BSB104\\n  BSA92\\n  BSB106\\n  BSA94\\n  ISA18\\n  CFA17\\n  ISI87\\n  BSB114\\n  ISA15\\n  BSB116\\n  ISB28\\n  BSB97\\n  CFA15\\n  ISA11\\n  ISB33\\n  BSA47\\n  ISB40\\n  ISB39\\n  CFA7\\n  CFA13\\n  ISS146\\n  ISB25\\n  BSA45\\n  BSB118\\n  CFA1\\n  CFS191\\n  ISB35\\n  CFB65\\n  CFA31\\n  BSB113\\n  ISB32\\n  ISA16\\n  CFS210\\n  BSA48\\n  BSA36\\n  ISI97\\n  CFA30\\n  CFA2\\n  CFB80\\n  CFA38\\n  CFA32\\n  ISA5\\n  BSA49\\n  CFB64\\n  __typename\\n}\\n\\nquery Query($ticker: String!, $period: String!) {\\n  CompanyFinancialRatio(ticker: $ticker, period: $period) {\\n    ratio {\\n      ...Ratios\\n      __typename\\n    }\\n    period\\n    __typename\\n  }\\n}\\n\",\"variables\":{\"ticker\":\"VCI\",\"period\":\"Q\"}}"