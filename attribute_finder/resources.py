import time
import requests
from attribute_finder.constant import *
from attribute_finder.type import IAnalysis_Report, ICompany, ICountry, IDeal, IFinance, IMacro
from vnstock3 import Vnstock
from datetime import date, timedelta
import pandas as pd
import pandas_ta as ta
import wbgapi as wb
import yfinance as yf

from config.config import Config
from utils.logger import Logger

tcbs_stock_api = Vnstock().stock(symbol='MSN', source="TCBS")
vci_stock_api = Vnstock().stock(symbol='MSN', source="VCI")
fx_stock_api = Vnstock().fx(symbol=USDVND, source='MSN')

logger = Logger(Config.log_level)

begin_date_trade = {}

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
        "time": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    })
    # Ensure 'Date' is a datetime object
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    return df

@add_ta_decorator
@load_chunk_time
def load_fx_online(symbol: str, date_begin: date, date_end: date, interval: str) -> pd.DataFrame:
    logger.info(f"loading fx data {symbol} from {date_begin} to {date_end} with interval {interval}")
    historical_data = fx_stock_api.quote.history(symbol=symbol, start=date_begin.isoformat(), end=date_end.isoformat(), interval=interval)
    df = vnstock_to_time_data(historical_data)
    return df

@add_ta_decorator
@load_chunk_time
def load_yahoo_finance_online(symbol: str, date_begin: date, date_end: date, interval: str) -> pd.DataFrame:
    logger.info(f"loading yahoo finance data {symbol} from {date_begin} to {date_end} with interval {interval}")
    ticker = yf.Ticker(symbol)
    historical_data = ticker.history(interval=interval, start=date_begin, end=date_end) 
    return historical_data

@add_ta_decorator
@load_chunk_time
def load_vnstock_online(symbol: str, date_begin: date, date_end: date, interval: str) -> pd.DataFrame:
    logger.info(f"loading vnstock data {symbol} from {date_begin} to {date_end} with interval {interval}")
    vci_stock_api.update_symbol(symbol)
    historical_data = vci_stock_api.quote.history(start=date_begin.isoformat(), end=date_end.isoformat(), interval=interval)
    df = vnstock_to_time_data(historical_data)
    return df

def load_world_bank_online(country: str, indicator: str, year_begin: int, year_end: int) -> dict[int, float]:
    logger.info(f"loading world bank data {indicator} for {country} from {year_begin} to {year_end}")
    if year_begin >= year_end:
        year_begin = year_end - 1
    for row in wb.data.fetch(indicator, country, range(year_begin, year_end)): 
        year = int(row['time'][-4:])
        return {year: row['value']}
    
def get_the_begin_date(symbol: str) -> date:
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

def load_analysis_report_online(symbol: str) -> dict[(date, str), IAnalysis_Report]:
    url = "https://api.simplize.vn/api/company/analysis-report/list"
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
        response = requests.get(url, params=params)
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

def load_macro_online(date_begin: date, date_end: date) -> IMacro:
    return IMacro(
        vnindex=load_company_online(VNINDEX, date_begin, date_end),
        vn_country=load_country_online(VIET_NAM_ID, date_begin.year, date_end.year),
        us_country=load_country_online(USA_ID, date_begin.year, date_end.year),
        china_country=load_country_online(CHINA_ID, date_begin.year, date_end.year),

        gold_day=load_yahoo_finance_online(GOLD, date_begin, date_end, '1d'),
        gold_month=load_yahoo_finance_online(GOLD, date_begin, date_end, '1mo'),
        oil_day=load_yahoo_finance_online(BRENT_OIL, date_begin, date_end, '1d'),
        oil_month=load_yahoo_finance_online(BRENT_OIL, date_begin, date_end, '1mo'),
        vix_day=load_yahoo_finance_online(VIX, date_begin, date_end, '1d'),

        dowjones_day=load_yahoo_finance_online(DOWJONES, date_begin, date_end, '1d'),
        sp500_day=load_yahoo_finance_online(SP500, date_begin, date_end, '1d'),
        shanghai_day=load_yahoo_finance_online(SHANGHAI, date_begin, date_end, '1d'),
        hang_seng_day=load_yahoo_finance_online(HANGSENG, date_begin, date_end, '1d'),
        nikkei_day=load_yahoo_finance_online(NIKKEI, date_begin, date_end, '1d'),
        kospi_day=load_yahoo_finance_online(KOSPI, date_begin, date_end, '1d'),
        btc_day=load_yahoo_finance_online(BTC, date_begin, date_end, '1d'),
        eth_day=load_yahoo_finance_online(ETH, date_begin, date_end, '1d'),
        dxy_day=load_yahoo_finance_online(DXY, date_begin, date_end, '1d'),
        dxy_month=load_yahoo_finance_online(DXY, date_begin, date_end, '1mo'),

        usd_day=load_fx_online(USDVND, date_begin, date_end, '1D'),
        usd_month=load_fx_online(USDVND, date_begin, date_end, '1M'),
        cny_day=load_fx_online(CNYVND, date_begin, date_end, '1D'),
        cny_month=load_fx_online(CNYVND, date_begin, date_end, '1M')
    )

def load_company_online(name: str, date_begin: date, date_end: date) -> ICompany:
    tcbs_stock_api.update_symbol(name)
    company_overview = tcbs_stock_api.company.overview()
    shareholders = tcbs_stock_api.company.shareholders()
    begin_date_trade[name] = get_the_begin_date(name)

    insider_data_res = tcbs_stock_api.company.insider_deals(page_size=100)
    insider_deals = [
        IDeal(
            deal_announce_date=row['deal_announce_date'].to_pydatetime(),
            deal_action=row['deal_action'],
            deal_quantity=row['deal_quantity'],
            deal_price=row['deal_price']
        ) for _, row in insider_data_res.iterrows()
    ]

    income_statement = tcbs_stock_api.finance.income_statement(period='quarter')
    balance_sheet = tcbs_stock_api.finance.balance_sheet(period='quarter')
    cash_flow = tcbs_stock_api.finance.cash_flow(period='quarter')
    ratio = tcbs_stock_api.finance.ratio(period='quarter')
    finance_data = cash_flow.merge(income_statement, on=['period'], suffixes=('_1', '_2')).merge(
        balance_sheet, on=['period'], suffixes=('_2', '_3')).merge(ratio, on=['period'], suffixes=('_3', '_4'))

    finances = {}
    for _, row in finance_data.iterrows():
        finances[(row.get('year_1'), row.get('quarter_1'))] = IFinance(
            quarter=row.get('quarter_1'),
            year=row.get('year_1'),
            revenue=row.get('revenue'),
            year_revenue_growth=row.get('year_revenue_growth'),
            quarter_revenue_growth=row.get('quarter_revenue_growth'),
            cost_of_good_sold=row.get('cost_of_good_sold'),
            gross_profit=row.get('gross_profit'),
            operation_expense=row.get('operation_expense'),
            operation_profit=row.get('operation_profit'),
            year_operation_profit_growth=row.get('year_operation_profit_growth'),
            quarter_operation_profit_growth=row.get('quarter_operation_profit_growth'),
            interest_expense=row.get('interest_expense'),
            pre_tax_profit=row.get('pre_tax_profit'),
            post_tax_profit=row.get('post_tax_profit'),
            share_holder_income=row.get('share_holder_income'),
            year_share_holder_income_growth=row.get('year_share_holder_income_growth'),
            quarter_share_holder_income_growth=row.get('quarter_share_holder_income_growth'),
            ebitda=row.get('ebitda'),
            # balance sheet
            short_asset=row.get('short_asset'),
            cash=row.get('cash'),
            short_invest=row.get('short_invest'),
            short_receivable=row.get('short_receivable'),
            inventory=row.get('inventory'),
            long_asset=row.get('long_asset'),
            fixed_asset=row.get('fixed_asset'),
            asset=row.get('asset'),
            debt=row.get('debt'),
            short_debt=row.get('short_debt'),
            long_debt=row.get('long_debt'),
            equity=row.get('equity'),
            capital=row.get('capital'),
            other_debt=row.get('other_debt'),
            un_distributed_income=row.get('un_distributed_income'),
            minor_share_holder_profit=row.get('minor_share_holder_profit'),
            payable=row.get('payable'),
            # cash flow
            invest_cost=row.get('invest_cost'),
            from_invest=row.get('from_invest'),
            from_financial=row.get('from_financial'),
            from_sale=row.get('from_sale'),
            free_cash_flow=row.get('free_cash_flow'),
            # ratio
            price_to_earning=row.get('price_to_earning'),
            price_to_book=row.get('price_to_book'),
            value_before_ebitda=row.get('value_before_ebitda'),
            roe=row.get('roe'),
            roa=row.get('roa'),
            days_receivable=row.get('days_receivable'),
            days_inventory=row.get('days_inventory'),
            days_payable=row.get('days_payable'),
            ebit_on_interest=row.get('ebit_on_interest'),
            earning_per_share=row.get('earning_per_share'),
            book_value_per_share=row.get('book_value_per_share'),
            equity_on_total_asset=row.get('equity_on_total_asset'),
            equity_on_liability=row.get('equity_on_liability'),
            current_payment=row.get('current_payment'),
            quick_payment=row.get('quick_payment'),
            eps_change=row.get('eps_change'),
            ebitda_on_stock=row.get('ebitda_on_stock'),
            gross_profit_margin=row.get('gross_profit_margin'),
            operating_profit_margin=row.get('operating_profit_margin'),
            post_tax_margin=row.get('post_tax_margin'),
            debt_on_equity=row.get('debt_on_equity'),
            debt_on_asset=row.get('debt_on_asset'),
            debt_on_ebitda=row.get('debt_on_ebitda'),
            short_on_long_debt=row.get('short_on_long_debt'),
            asset_on_equity=row.get('asset_on_equity'),
            capital_balance=row.get('capital_balance'),
            cash_on_equity=row.get('cash_on_equity'),
            cash_on_capitalize=row.get('cash_on_capitalize'),
            cash_circulation=row.get('cash_circulation'),
            revenue_on_work_capital=row.get('revenue_on_work_capital'),
            capex_on_fixed_asset=row.get('capex_on_fixed_asset'),
            revenue_on_asset=row.get('revenue_on_asset'),
            post_tax_on_pre_tax=row.get('post_tax_on_pre_tax'),
            ebit_on_revenue=row.get('ebit_on_revenue'),
            pre_tax_on_ebit=row.get('pre_tax_on_ebit'),
            payable_on_equity=row.get('payable_on_equity'),
            ebitda_on_stock_change=row.get('ebitda_on_stock_change'),
            book_value_per_share_change=row.get('book_value_per_share_change')
        )

    return ICompany(
        name=name,
        exchange=company_overview.at[0, 'exchange'],
        begin_trade_date=begin_date_trade[name],
        industry_id=company_overview.at[0, 'industry_id'],
        industry_id_v2=company_overview.at[0, 'industry_id_v2'],
        established_year=company_overview.at[0, 'established_year'],
        top_1_shareholders=shareholders.at[0, 'share_holder'],
        top_2_shareholder=shareholders.at[1, 'share_holder'],
        others_shareholders_percent=shareholders.iloc[-1]['share_own_percent'],
        day_points=load_vnstock_online(name, date_begin, date_end, '1D'),
        week_points=load_vnstock_online(name, date_begin, date_end, '1W'),
        month_points=load_vnstock_online(name, date_begin, date_end, '1M'),
        insider_deals=insider_deals,
        finances=finances,
        analysis_reports=load_analysis_report_online(name)
    )

def get_company_equity(symbol: str) -> float:
    vci_stock_api.update_symbol(symbol)
    balance_sheet = vci_stock_api.finance.balance_sheet(period='quarter')
    first_row = balance_sheet.iloc[0]
    return first_row["OWNER'S EQUITY(Bn.VND)"] / 1000000000

def get_company_average_volume(symbol: str) -> float:
    vci_stock_api.update_symbol(symbol)
    current_date = date.today()
    begin_date = current_date - timedelta(days=30)
    historical_data = vci_stock_api.quote.history(start=begin_date.isoformat(), end=current_date.isoformat(), interval='1D')
    return (historical_data['volume'].mean() * historical_data['close'].mean()) / 1000000
    
def get_company_list() -> list[str]:
    result = []
    companies = vci_stock_api.listing.all_symbols()
    for _, row in companies.iterrows():
        symbol = row['ticker']
        try:
            equity = get_company_equity(symbol)
            if equity < 1000:
                continue
            average_volume = get_company_average_volume(symbol)
            if average_volume < 1:
                continue
        except Exception as e:
            logger.error(f"cannot load company {symbol} ", e)
            continue
        print(symbol, equity, average_volume)
            
        result.append(symbol)
    
    # save to file
    with open('company_list.txt', 'w') as f:
        for item in result:
            f.write("%s\n" % item)
    return result