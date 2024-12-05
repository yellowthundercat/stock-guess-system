from attribute_finder.constant import *
from attribute_finder.type import ICompany, ICountry, IDeal, IFinance, IMacro
from vnstock3 import Vnstock
from datetime import date
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

def add_ta(df: pd.DataFrame) -> pd.DataFrame:
    # TA: Technical Analysis
    my_strategy = ta.Strategy(
        name="My Combined Strategy",
        ta=[
            {"kind": "sma", "length": 50},             # SMA 50
            {"kind": "sma", "length": 200},            # SMA 200
            {"kind": "bbands", "length": 20},          # Bollinger Bands
            {"kind": "rsi", "length": 14},             # RSI
            {"kind": "macd", "fast": 12, "slow": 26, "signal": 9},  # MACD
            {"kind": "sma", "close": "volume", "length": 20},       # Volume SMA 20
            {"kind": "stoch", "k": 14, "d": 3}         # Stochastic Oscillator
        ]
    )
    df.ta.strategy(my_strategy)
    return df

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

def load_fx_online(symbol: str, date_begin: date, date_end: date, interval: str) -> pd.DataFrame:
    logger.info(f"loading fx data {symbol} from {date_begin} to {date_end} with interval {interval}")
    historical_data = fx_stock_api.quote.history(symbol=symbol, start=date_begin.isoformat(), end=date_end.isoformat(), interval=interval)
    df = vnstock_to_time_data(historical_data)
    return df

def load_yahoo_finance_online(symbol: str, date_begin: date, date_end: date, interval: str) -> pd.DataFrame:
    logger.info(f"loading yahoo finance data {symbol} from {date_begin} to {date_end} with interval {interval}")
    ticker = yf.Ticker(symbol)
    historical_data = ticker.history(interval=interval, start=date_begin, end=date_end) 
    df = add_ta(historical_data) if interval == '1d' else historical_data
    return df

def load_vnstock_online(symbol: str, date_begin: date, date_end: date, interval: str) -> pd.DataFrame:
    logger.info(f"loading vnstock data {symbol} from {date_begin} to {date_end} with interval {interval}")
    vci_stock_api.update_symbol(symbol)
    historical_data = vci_stock_api.quote.history(start=date_begin.isoformat(), end=date_end.isoformat(), interval=interval)
    df = vnstock_to_time_data(historical_data)
    df = add_ta(df) if interval == '1D' else df
    return df

def load_world_bank_online(country: str, indicator: str, year_begin: int, year_end: int) -> dict[int, float]:
    logger.info(f"loading world bank data {indicator} for {country} from {year_begin} to {year_end}")
    if year_begin >= year_end:
        year_begin = year_end - 1
    for row in wb.data.fetch(indicator, country, range(year_begin, year_end)): 
        year = int(row['time'][-4:])
        return {year: row['value']}

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
        finances[(row['year_1'], row['quarter_1'])] = IFinance(
            quarter=row['quarter_1'],
            year=row['year_1'],
            revenue=row['revenue'],
            year_revenue_growth=row['year_revenue_growth'],
            quarter_revenue_growth=row['quarter_revenue_growth'],
            cost_of_good_sold=row['cost_of_good_sold'],
            gross_profit=row['gross_profit'],
            operation_expense=row['operation_expense'],
            operation_profit=row['operation_profit'],
            year_operation_profit_growth=row['year_operation_profit_growth'],
            quarter_operation_profit_growth=row['quarter_operation_profit_growth'],
            interest_expense=row['interest_expense'],
            pre_tax_profit=row['pre_tax_profit'],
            post_tax_profit=row['post_tax_profit'],
            share_holder_income=row['share_holder_income'],
            year_share_holder_income_growth=row['year_share_holder_income_growth'],
            quarter_share_holder_income_growth=row['quarter_share_holder_income_growth'],
            ebitda=row['ebitda'],
            # balance sheet
            short_asset=row['short_asset'],
            cash=row['cash'],
            short_invest=row['short_invest'],
            short_receivable=row['short_receivable'],
            inventory=row['inventory'],
            long_asset = row['long_asset'],
            fixed_asset = row['fixed_asset'],
            asset = row['asset'],
            debt = row['debt'],
            short_debt = row['short_debt'],
            long_debt = row['long_debt'],
            equity=row['equity'],
            capital=row['capital'],
            other_debt=row['other_debt'],
            un_distributed_income=row['un_distributed_income'],
            minor_share_holder_profit=row['minor_share_holder_profit'],
            payable=row['payable'],
            # cash flow
            invest_cost=row['invest_cost'],
            from_invest=row['from_invest'],
            from_financial=row['from_financial'],
            from_sale=row['from_sale'],
            free_cash_flow=row['free_cash_flow'],
            # ratio
            price_to_earning=row['price_to_earning'],
            price_to_book=row['price_to_book'],
            value_before_ebitda=row['value_before_ebitda'],
            roe=row['roe'],
            roa=row['roa'],
            days_receivable=row['days_receivable'],
            days_inventory=row['days_inventory'],
            days_payable=row['days_payable'],
            ebit_on_interest=row['ebit_on_interest'],
            earning_per_share=row['earning_per_share'],
            book_value_per_share=row['book_value_per_share'],
            equity_on_total_asset=row['equity_on_total_asset'],
            equity_on_liability=row['equity_on_liability'],
            current_payment=row['current_payment'],
            quick_payment=row['quick_payment'],
            eps_change=row['eps_change'],
            ebitda_on_stock=row['ebitda_on_stock'],
            gross_profit_margin=row['gross_profit_margin'],
            operating_profit_margin=row['operating_profit_margin'],
            post_tax_margin=row['post_tax_margin'],
            debt_on_equity=row['debt_on_equity'],
            debt_on_asset=row['debt_on_asset'],
            debt_on_ebitda=row['debt_on_ebitda'],
            short_on_long_debt=row['short_on_long_debt'],
            asset_on_equity=row['asset_on_equity'],
            capital_balance=row['capital_balance'],
            cash_on_equity=row['cash_on_equity'],
            cash_on_capitalize=row['cash_on_capitalize'],
            cash_circulation=row['cash_circulation'],
            revenue_on_work_capital=row['revenue_on_work_capital'],
            capex_on_fixed_asset=row['capex_on_fixed_asset'],
            revenue_on_asset=row['revenue_on_asset'],
            post_tax_on_pre_tax=row['post_tax_on_pre_tax'],
            ebit_on_revenue=row['ebit_on_revenue'],
            pre_tax_on_ebit=row['pre_tax_on_ebit'],
            payable_on_equity=row['payable_on_equity'],
            ebitda_on_stock_change=row['ebitda_on_stock_change'],
            book_value_per_share_change=row['book_value_per_share_change']
        )

    return ICompany(
        name=name,
        exchange=company_overview.at[0, 'exchange'],
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
        finances=finances
    )

# analysis report https://api.simplize.vn/api/company/analysis-report/list?ticker=MSN&isWl=false&page=1&size=10
