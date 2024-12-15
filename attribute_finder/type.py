from dataclasses import dataclass
from datetime import date

from pandas import DataFrame

@dataclass
class IDeal:
    deal_announce_date: date 
    deal_action: str  
    deal_quantity: int  
    deal_price: float

@dataclass
class IFinance:
    # income statement
    quarter: int
    year: int
    revenue: float
    year_revenue_growth: float
    quarter_revenue_growth: float
    cost_of_good_sold: int 
    gross_profit: int 
    operation_expense: int 
    operation_profit: int 
    year_operation_profit_growth: float
    quarter_operation_profit_growth: float
    interest_expense: int 
    pre_tax_profit: int 
    post_tax_profit: int 
    share_holder_income: int 
    year_share_holder_income_growth: float
    quarter_share_holder_income_growth: float
    ebitda: float
    # balance sheet
    short_asset: int 
    cash: int 
    short_invest: int 
    short_receivable: int 
    inventory: int 
    long_asset: int 
    fixed_asset: int 
    asset: int 
    debt: int 
    short_debt: int 
    long_debt: int 
    equity: int 
    capital: int 
    other_debt: int 
    un_distributed_income: int 
    minor_share_holder_profit: int 
    payable: int 
    # cash flow
    invest_cost: int 
    from_invest: int 
    from_financial: int 
    from_sale: int 
    free_cash_flow: float
    # ratio
    price_to_earning: float
    price_to_book: float
    value_before_ebitda: float
    roe: float
    roa: float
    days_receivable: float
    days_inventory: float
    days_payable: int
    ebit_on_interest: float
    earning_per_share: int
    book_value_per_share: int
    equity_on_total_asset: float
    equity_on_liability: float
    current_payment: float
    quick_payment: float
    eps_change: float
    ebitda_on_stock: int
    gross_profit_margin: float
    operating_profit_margin: float
    post_tax_margin: float
    debt_on_equity: float
    debt_on_asset: float
    debt_on_ebitda: float
    short_on_long_debt: float
    asset_on_equity: float
    capital_balance: int
    cash_on_equity: float
    cash_on_capitalize: float
    cash_circulation: float
    revenue_on_work_capital: float
    capex_on_fixed_asset: float
    revenue_on_asset: float
    post_tax_on_pre_tax: float
    ebit_on_revenue: float
    pre_tax_on_ebit: float
    payable_on_equity: float
    ebitda_on_stock_change: float
    book_value_per_share_change: float

@dataclass
class IAnalysis_Report:
    source: str
    issueDate: date
    targetPrice: int
    recommend: str


@dataclass
class ICompany:
    name: str
    begin_trade_date: date
    exchange: str
    industry_id: str
    industry_id_v2: str
    established_year: str
    top_1_shareholders: str
    top_2_shareholder: str
    others_shareholders_percent: float

    day_points: DataFrame
    week_points: DataFrame
    month_points: DataFrame

    insider_deals: list[IDeal]
    finances: dict[tuple[int, int], IFinance] # year, quarter
    analysis_reports: dict[(date, str), IAnalysis_Report] # date, source


@dataclass
class ICountry:
    name: str
    # year, value
    gdq_growth: dict[int, float]
    real_interest_rate: dict[int, float]
    unemployment_rate: dict[int, float]
    inflation: dict[int, float]
    current_account_balance: dict[int, float]
    government_debt: dict[int, float]

@dataclass
class IMacro:
    # vietnam
    vnindex: ICompany
    # forex
    usd_day: DataFrame
    usd_month: DataFrame
    cny_day: DataFrame
    cny_month: DataFrame
    # country
    vn_country: ICountry
    us_country: ICountry
    china_country: ICountry
    # yahoo finance
    gold_day: DataFrame
    gold_month: DataFrame
    oil_day: DataFrame
    oil_month: DataFrame
    vix_day: DataFrame
    dxy_day: DataFrame
    dxy_month: DataFrame

    dowjones_day: DataFrame
    sp500_day: DataFrame
    shanghai_day: DataFrame
    hang_seng_day: DataFrame
    nikkei_day: DataFrame
    kospi_day: DataFrame
    btc_day: DataFrame
    eth_day: DataFrame
