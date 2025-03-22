import datetime
import json
import time
import requests
from attribute_finder.constant import *
from attribute_finder.type import IAnalysis_Report, ICompany, ICountry, IDeal, IMacro
from vnstock3 import Vnstock
from datetime import date, timedelta
import pandas as pd
import pandas_ta as ta
import wbgapi as wb
import yfinance as yf
from dateutil.relativedelta import relativedelta

from config.config import Config
from utils.logger import Logger


from vnstock3.explorer.fmarket.fund import Fund

from utils.utils import as_df, get_header

tcbs_stock_api = Vnstock().stock(symbol='MSN', source="TCBS")
vci_stock_api = Vnstock().stock(symbol='MSN', source="VCI")
# fx_stock_api = Vnstock().fx(symbol=USDVND, source='MSN')

logger = Logger(Config.log_level)

begin_date_trade = {}

VCI_HEADER = get_header()

SIMPLIZE_URL = "https://api.simplize.vn/api/company/analysis-report/list"

def add_ta(df: pd.DataFrame) -> pd.DataFrame:
    # TA: Technical Analysis
    my_strategy = ta.Strategy(
        name="My Combined Strategy",
        ta=[
            {"kind": "sma", "length": 50},             # SMA 50
            {"kind": "sma", "length": 200},            # SMA 200
            {"kind": "bbands", "length": 20},          # Bollinger Bands
            {"kind": "rsi", "length": 14},             # RSI
            # {"kind": "macd", "fast": 12, "slow": 26, "signal": 9},  # MACD
            {"kind": "sma", "close": "volume", "length": 20},       # Volume SMA 20
            {"kind": "stoch", "k": 14, "d": 3}         # Stochastic Oscillator
        ]
    )
    df.ta.strategy(my_strategy) 
    return df

def retry(func):
    def inner(*args, **kwargs):
        for i in range(3):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"retry {func.__name__} {i} times", e)
                time.sleep(1)
        raise ConnectionError(f"Cannot load data from {func.__name__}")
    return inner

def load_chunk_time(real_func):
    def inner(symbol: str, date_begin: date, date_end: date, interval: str) -> pd.DataFrame:
        stock_begin = begin_date_trade.get(symbol, date(2010, 1, 1))
        if date_end < stock_begin:
            return pd.DataFrame()
        if date_begin < stock_begin:
            date_begin = stock_begin
        
        lower_interval = interval.lower()
        # check interval contain d
        if 'd' in lower_interval:
            period = (date_end - date_begin).days
            step = 1
        if 'w' in lower_interval:
            period = (date_end - date_begin).days//7
            step = 7
        if 'm' in lower_interval:
            period = (date_end - date_begin).days//30
            step = 30
        if 'y' in lower_interval:
            real_func(symbol, date_begin, date_end, interval)
        chunk_size = LOAD_TIME_DATA_CHUNK_SIZE
        if period > chunk_size:
            chunks = [date_begin + timedelta(days=-1)]
            for _ in range(1, period//chunk_size):
                chunks.append(chunks[-1] + timedelta(days=chunk_size*step))
            chunks.append(date_end)
            return pd.concat([real_func(symbol, chunks[i] + timedelta(days=1), chunks[i+1], interval) for i in range(len(chunks)-1)])
        else:
            return real_func(symbol, date_begin, date_end, interval)
    return inner

def add_ta_decorator(real_func):
    def inner(symbol: str, date_begin: date, date_end: date, interval: str):
        df = real_func(symbol, date_begin, date_end, interval)
        return add_ta(df) if df.shape[0] > 20 else df
    return inner

def vnstock_to_time_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={
        "time": DATE,
        "open": OPEN,
        "high": HIGH,
        "low": LOW,
        "close": CLOSE,
        "volume": VOLUME
    })
    # Ensure 'Date' is a panda datetime object
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    return df

@load_chunk_time
@retry
def load_fx_online(symbol: str, date_begin: date, date_end: date, interval: str) -> pd.DataFrame:
    logger.info(f"loading fx data {symbol} from {date_begin} to {date_end} with interval {interval}")
    historical_data = fx_stock_api.quote.history(symbol=symbol, start=date_begin.isoformat(), end=date_end.isoformat(), interval=interval)
    df = vnstock_to_time_data(historical_data)
    return df

@load_chunk_time
@retry
def load_yahoo_finance_online(symbol: str, date_begin: date, date_end: date, interval: str) -> pd.DataFrame:
    logger.info(f"loading yahoo finance data {symbol} from {date_begin} to {date_end} with interval {interval}")
    ticker = yf.Ticker(symbol)
    df = ticker.history(interval=interval, start=date_begin, end=date_end) 
    # remove localize timezone
    df.index = df.index.tz_localize(None)
    return df

@load_chunk_time
@retry
def load_vnstock_online(symbol: str, date_begin: date, date_end: date, interval: str) -> pd.DataFrame:
    logger.info(f"loading vnstock data {symbol} from {date_begin} to {date_end} with interval {interval}")
    historical_data = vci_stock_api.quote.history(symbol=symbol, start=date_begin.isoformat(), end=date_end.isoformat(), interval=interval)
    df = vnstock_to_time_data(historical_data)
    return df

@retry
def load_world_bank_online(country: str, indicator: str, year_begin: int, year_end: int) -> dict[int, float]:
    logger.info(f"loading world bank data {indicator} for {country} from {year_begin} to {year_end}")
    if year_begin >= year_end:
        year_begin = year_end - 1
    result = {}
    for row in wb.data.fetch(indicator, country, range(year_begin, year_end)): 
        year = int(row['time'][-4:])
        result[year] = row['value']
    return result
    
@retry
def get_the_begin_date(symbol: str) -> date:
    if symbol == 'VHM':
        return date(2019, 1, 1)
    left_date = date(2010, 1, 1)
    right_date = date.today()
    while left_date < right_date:
        current_date = left_date + (right_date - left_date)//2
        try:
            load_vnstock_online(symbol, current_date, current_date + timedelta(days=1), '1D')
            right_date = current_date
        except Exception as e:
            left_date = current_date + timedelta(days=1)

    logger.info(f"the begin date of {symbol} is {right_date}")
    return right_date

@retry
def load_analysis_report_online(symbol: str) -> dict[(date, str), IAnalysis_Report]:
    result = {}
    page_number = 0
    while True:
        params = {
            "ticker": symbol,
            "isWl": "false",
            "page": page_number,
            "size": CHUNK_SIZE
        }
        page_number += 1
        response = requests.get(SIMPLIZE_URL, params=params)
        if response.status_code == 200:
            res = response.json()
            total = res['total']
            data = res['data']
            result.update({
                (row['issueDate'],row['source']) : IAnalysis_Report(
                    source=row['source'],
                    issueDate=row['issueDate'],
                    targetPrice=row.get('targetPrice', 0),
                    recommend=row['recommend']
                ) for row in data
            })
            if page_number*CHUNK_SIZE >= total:
                break
        else:
            logger.error(f"cannot load analysis report for {symbol}, status code {response.status_code}")
            break

    logger.info(f"loaded {len(result)} analysis reports for {symbol}")
    return result

@retry
def load_country_online(country: str, year_begin: int, year_end: int) -> ICountry:
    return ICountry(
        name=country,
        gdq_growth=load_world_bank_online(country, GDP_GROWTH, year_begin, year_end),
        real_interest_rate=load_world_bank_online(country, REAL_INTEREST_RATE, year_begin, year_end),
        unemployment_rate=load_world_bank_online(country, UNEMPLOYMENT_RATE, year_begin, year_end),
        inflation=load_world_bank_online(country, INFLATION, year_begin, year_end),
        current_account_balance=load_world_bank_online(country, CURRENT_ACCOUNT_BALANCE, year_begin, year_end),
        government_debt=load_world_bank_online(country, GOVERNMENT_DEBT, year_begin, year_end)
    )

@retry
def load_macro_online(date_begin: date, date_end: date, extend_date_begin: date) -> IMacro:
    return IMacro(
        vnindex=load_company_online(VNINDEX, date_begin, date_end, extend_date_begin),
        vn_country=load_country_online(VIET_NAM_ID, extend_date_begin.year, date_end.year),
        us_country=load_country_online(USA_ID, extend_date_begin.year, date_end.year),
        china_country=load_country_online(CHINA_ID, extend_date_begin.year, date_end.year),

        gold_day=load_yahoo_finance_online(GOLD, date_begin, date_end, '1d'),
        gold_month=load_yahoo_finance_online(GOLD, extend_date_begin, date_end, '1mo'),
        oil_day=load_yahoo_finance_online(BRENT_OIL, date_begin, date_end, '1d'),
        oil_month=load_yahoo_finance_online(BRENT_OIL, extend_date_begin, date_end, '1mo'),

        dowjones_day=load_yahoo_finance_online(DOWJONES, date_begin, date_end, '1d'),
        sp500_day=load_yahoo_finance_online(SP500, date_begin, date_end, '1d'),
        shanghai_day=load_yahoo_finance_online(SHANGHAI, date_begin, date_end, '1d'),
        hang_seng_day=load_yahoo_finance_online(HANGSENG, date_begin, date_end, '1d'),
        nikkei_day=load_yahoo_finance_online(NIKKEI, date_begin, date_end, '1d'),
        kospi_day=load_yahoo_finance_online(KOSPI, date_begin, date_end, '1d'),
        btc_day=load_yahoo_finance_online(BTC, date_begin, date_end, '1d'),
        dxy_day=load_yahoo_finance_online(DXY, date_begin, date_end, '1d'),
        dxy_month=load_yahoo_finance_online(DXY, extend_date_begin, date_end, '1mo'),

        usd_day=load_fx_online(USDVND, date_begin, date_end, '1D'),
        usd_month=load_fx_online(USDVND, extend_date_begin, date_end, '1M'),
        cny_day=load_fx_online(CNYVND, date_begin, date_end, '1D'),
        cny_month=load_fx_online(CNYVND, extend_date_begin, date_end, '1M')
    )

def format_financial_data(df: pd.DataFrame, extracted_columns: list) -> pd.DataFrame:
    for col in extracted_columns:
        if col not in df.columns:
            df[col] = 0
    return df[extracted_columns]

@retry
def load_company_online(name: str, date_begin: date, date_end: date, extend_date_begin: date) -> ICompany:
    tcbs_stock_api.update_symbol(name)
    company_overview = tcbs_stock_api.company.overview()
    shareholders = tcbs_stock_api.company.shareholders()
    begin_date_trade[name] = get_the_begin_date(name)

    try:
        insider_data_res = tcbs_stock_api.company.insider_deals(page_size=100)
        insider_deals = [
            IDeal(
                deal_announce_date=row['deal_announce_date'].to_pydatetime(),
                deal_action=row['deal_action'],
                deal_quantity=row['deal_quantity'],
                deal_price=row['deal_price']
            ) for _, row in insider_data_res.iterrows()
        ]
    except Exception as e:
        logger.error(f"cannot load insider deals for {name}", e)
        insider_deals = []

    income_statement = tcbs_stock_api.finance.income_statement(period='quarter')
    extract_columns = [ 'quarter', 'year',
                        'revenue', 'year_revenue_growth', 'cost_of_good_sold', 'gross_profit',
                        'operation_expense', 'operation_profit', 'year_operation_profit_growth',
                        'interest_expense', 'pre_tax_profit', 'post_tax_profit', 'share_holder_income', 'ebitda']
    income_statement = format_financial_data(income_statement, extract_columns)
    balance_sheet = tcbs_stock_api.finance.balance_sheet(period='quarter')
    extract_columns = ['short_asset', 'cash', 'short_invest', 'short_receivable', 'inventory', 'long_asset',
                       'fixed_asset', 'asset', 'debt', 'short_debt', 'long_debt', 'equity', 'capital', 'un_distributed_income',
                       'minor_share_holder_profit', 'payable']
    balance_sheet = format_financial_data(balance_sheet, extract_columns)
    cash_flow = tcbs_stock_api.finance.cash_flow(period='quarter')
    extract_columns = ['invest_cost', 'from_invest', 'from_financial', 'from_sale', 'free_cash_flow']
    cash_flow = format_financial_data(cash_flow, extract_columns)
    ratio = tcbs_stock_api.finance.ratio(period='quarter')
    # ratio['quarter'] = ratio['quarter'].astype(str) # convert to string for merging
    extract_columns = ['price_to_earning', 'price_to_book', 'roe', 'roa', 'equity_on_liability',
                   'gross_profit_margin', 'operating_profit_margin', 'debt_on_equity', 'cash_on_equity']
    ratio = format_financial_data(ratio, extract_columns)
    merged_df = pd.merge(income_statement, balance_sheet, on=['period'], how='inner')
    merged_df = pd.merge(merged_df, cash_flow, on=['period'], how='inner')
    merged_df = pd.merge(merged_df, ratio, on=['period'], how='inner')

    return ICompany(
        name=name,
        exchange=company_overview.at[0, 'exchange'],
        begin_trade_date=begin_date_trade[name],
        industry_id=company_overview.at[0, 'industry_id'],
        industry_id_v2=company_overview.at[0, 'industry_id_v2'],
        established_year=company_overview.at[0, 'established_year'],
        # top_1_shareholders=shareholders.at[0, 'share_holder'],
        # top_2_shareholder=shareholders.at[1, 'share_holder'],
        others_shareholders_percent=shareholders.iloc[-1]['share_own_percent'],
        day_points=add_ta(load_vnstock_online(name, extend_date_begin, date_end, '1D')),
        # week_points=load_vnstock_online(name, date_begin, date_end, '1W'),
        month_points=load_vnstock_online(name, extend_date_begin, date_end, '1M'),
        insider_deals=insider_deals,
        finances=merged_df,
        analysis_reports=load_analysis_report_online(name)
    )

@retry
def get_company_equity(symbol: str) -> float:
    vci_stock_api.update_symbol(symbol)
    balance_sheet = vci_stock_api.finance.balance_sheet(period='quarter')
    first_row = balance_sheet.iloc[0]
    return first_row["OWNER'S EQUITY(Bn.VND)"] / 1000000000

@retry
def get_company_average_volume(symbol: str) -> float:
    vci_stock_api.update_symbol(symbol)
    current_date = date.today()
    begin_date = current_date - timedelta(days=30)
    historical_data = vci_stock_api.quote.history(start=begin_date.isoformat(), end=current_date.isoformat(), interval='1D')
    return (historical_data['volume'].mean() * historical_data['close'].mean()) / 1000000
    
@retry
def get_company_list(min_equity: float, min_volume: float) -> list[str]:
    result = []
    companies = vci_stock_api.listing.all_symbols()
    for _, row in companies.iterrows():
        symbol = row['ticker']
        try:
            equity = get_company_equity(symbol)
            if equity < min_equity:
                continue
            average_volume = get_company_average_volume(symbol)
            if average_volume < min_volume:
                continue
        except Exception as e:
            logger.error(f"cannot load company {symbol} ", e)
            continue
        print(symbol, equity, average_volume)
            
        result.append(symbol)

    return result

# by fund and vn100
@retry
def get_invested_companies() -> dict[str, int]:
    fund = Fund()
    result = dict()
    companies = list(vci_stock_api.listing.symbols_by_group('VN100'))
    for c in companies:
        result[c] = 1

    funds = fund.listing('STOCK')
    for f in funds['short_name']:
        top_companies = fund.details.top_holding(f)
        # check exist stock code
        if 'stock_code' not in top_companies.columns:
            continue
        for c in top_companies['stock_code']:
            result[c] = result.get(c, 0) + 1
    return result

# get pe, pb and its mean value (5 years) for invested companies
@retry
def get_company_p(symbol: str) -> tuple[float, float, float, float, float, float, float]:
    current_date = date.today()
    vci_stock_api.update_symbol(symbol)
    ratio = vci_stock_api.finance.ratio(period='year', lang='vi') 

    price_df = load_vnstock_online(symbol, current_date - timedelta(days=30), current_date, '1D')
    price = price_df.iloc[-1][CLOSE]

    try:
        ratio_quarter = vci_stock_api.finance.ratio(period='quarter', lang='vi')
        current_pe = ratio_quarter.iloc[0][('Chỉ tiêu định giá', 'P/E')]
        current_pb = ratio_quarter.iloc[0][('Chỉ tiêu định giá', 'P/B')]
    except Exception as e:
        logger.error(f"cannot load current pe, pb for {symbol}", e)
        current_pe = ratio.iloc[0][('Chỉ tiêu định giá', 'P/E')]
        current_pb = ratio.iloc[0][('Chỉ tiêu định giá', 'P/B')]

    sum_pe = 0
    sum_pb = 0
    count = 0
    
    for _, row in ratio.iterrows():
        year = row[('Meta', 'Năm')]
        if year < current_date.year - 10:
            break
        count += 1
        sum_pe += row[('Chỉ tiêu định giá', 'P/E')]
        sum_pb += row[('Chỉ tiêu định giá', 'P/B')]

    # get lowest price in last 5 days
    lowest_week = price_df.tail(5).min()[CLOSE]
    lowest_month = price_df.min()[CLOSE]
    
    if count == 0:
        return current_pe, current_pb, 0, 0, price, lowest_week, lowest_month
    return current_pe, current_pb, sum_pe / count, sum_pb / count, price, lowest_week, lowest_month

@retry
def get_recommend_price(symbol: str) -> float:
    current_date = date.today()
    params = {
        "ticker": symbol,
        "isWl": "false",
        "page": 0,
        "size": 10
    }
    response = requests.get(SIMPLIZE_URL, params=params)
    if response.status_code == 200:
        res = response.json()
        sum_price = 0
        count = 0
        data = res['data']
        for row in data:
            if 'targetPrice' not in row or 'issueDate' not in row:
                continue
            issue_date = datetime.datetime.strptime(row['issueDate'], "%d/%m/%Y").date()
            if current_date > issue_date + timedelta(days=90):
                continue
            
            sum_price += row['targetPrice']
            count += 1
        return sum_price / count / 1000 if count > 0 else 0
    return 0


@retry
def manual_load_quote(symbol: str, date_begin: datetime.datetime, date_end: datetime.datetime, interval: str) -> pd.DataFrame:
    logger.info(f"loading vnstock data {symbol} from {date_begin} to {date_end} with interval {interval}")

    url = TRADING_URL + CHART_URL 

    payload = json.dumps({
        "timeFrame": INTERVAL_MAP[interval],
        "symbols": [symbol],
        "from": int(date_begin.timestamp()),
        "to": int(date_end.timestamp())
        })
    
    response = requests.post(url, headers=VCI_HEADER, data=payload)

    if response.status_code != 200:
        raise ConnectionError(f"Failed to fetch data: {response.status_code} - {response.reason}")
    json_data = response.json()
    if not json_data:
            raise ValueError("Không tìm thấy dữ liệu. Vui lòng kiểm tra lại mã chứng khoán hoặc thời gian truy xuất.")
    
    df = as_df(history_data=json_data[0], interval=interval)
    df = vnstock_to_time_data(df)
    return df

# signal: volume spike, rsi 30, 70, MACD
@retry
def get_anomaly_signal(symbol: str) -> tuple[float, float, bool, bool, bool]:
    current_date = pd.Timestamp.today().normalize()
    start_date = current_date - relativedelta(months=2)
    try:
        df = manual_load_quote(symbol, start_date.to_pydatetime(), current_date.to_pydatetime(), '1D')
        my_strategy = ta.Strategy(
            name="My Combined Strategy",
            ta=[
                {"kind": "rsi", "length": 14},             # RSI
                {"kind": "macd", "fast": 12, "slow": 26, "signal": 9},  # MACD
                {"kind": "sma", "close": "volume", "length": 20},       # Volume SMA 20
                {"kind": "sma", "close": "volume", "length": 5},       # Volume SMA 5
            ]
        )
    
        df.ta.strategy(my_strategy)
    
        is_volume_spike = 0
        is_volume_increase = 0
        is_rsi_30 = False
        is_rsi_70 = False
        is_macd_cross = False
        for i in pd.date_range(current_date - relativedelta(days=6), current_date):
            if i not in df.index:
                continue
            if df.at[i, 'Volume'] > df.at[i, 'SMA_20'] * 3:
                is_volume_spike = max(is_volume_spike, df.at[i, 'Volume']/df.at[i, 'SMA_20'])
            if df.at[i, 'SMA_5'] > df.at[i, 'SMA_20'] * 2:
                is_volume_increase = max(is_volume_increase, df.at[i, 'SMA_5']/df.at[i, 'SMA_20'])
            if df.at[i, 'RSI_14'] < 30:
                is_rsi_30 = True
            if df.at[i, 'RSI_14'] > 70:
                is_rsi_70 = True
            previous_i = df.index.get_loc(i) - 1
            if df.at[i, 'MACDh_12_26_9'] * df.iloc[previous_i]['MACDh_12_26_9'] < 0:
                is_macd_cross = True
    except Exception as e:
        logger.error(f"cannot load anomaly signal for {symbol}", e)
        return 0, 0, False, False, False 
    return is_volume_spike, is_volume_increase, is_rsi_30, is_rsi_70, is_macd_cross