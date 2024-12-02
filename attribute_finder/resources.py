from attribute_finder.type import ICompany, IDay_data, IDeal, IFinance, IMacro, IMonth_data, IWeek_data
from vnstock3 import Vnstock
from datetime import date
import pandas as pd


tcbs_stock_api = Vnstock().stock(symbol='MSN', source="TCBS")
vci_stock_api = Vnstock().stock(symbol='MSN', source="VCI")
# microsoft_stock_api = Vnstock().stock(symbol='MSN', source="MSN")

def load_macro_online(date_begin: date, date_end: date) -> IMacro:
    return IMacro()

def load_company_online(name: str, date_begin: date, date_end: date) -> ICompany:
    tcbs_stock_api.update_symbol(name)
    company_overview = tcbs_stock_api.company.overview()
    shareholders = tcbs_stock_api.company.shareholders()

    day_data = {}
    week_data = {}
    month_data = {}

    day_data_res = vci_stock_api.quote.history(symbol=name, start=date_begin.isoformat(), end=date_end.isoformat())
    for _, row in day_data_res.iterrows():
        time = row['time'].to_pydatetime()
        day_data[time] = IDay_data(
            open=row['open'],
            close=row['close'],
            high=row['high'],
            low=row['low'],
            volume=row['volume']
        )
    
    week_data_res = vci_stock_api.quote.history(symbol=name, start=date_begin.isoformat(), end=date_end.isoformat(), interval='1W')
    for _, row in week_data_res.iterrows():
        time = row['time'].to_pydatetime()
        week_data[time] = IWeek_data(
            open=row['open'],
            close=row['close'],
            high=row['high'],
            low=row['low'],
            volume=row['volume']
        )

    month_data_res = vci_stock_api.quote.history(symbol=name, start=date_begin.isoformat(), end=date_end.isoformat(), interval='1M')
    for _, row in month_data_res.iterrows():
        time = row['time'].to_pydatetime()
        month_data[time] = IMonth_data(
            open=row['open'],
            close=row['close'],
            high=row['high'],
            low=row['low'],
            volume=row['volume']
        )

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
        day_points=day_data,
        week_points=week_data,
        month_points=month_data,
        insider_deals=insider_deals,
        finances=finances
    )

# more data https://github.com/tradingeconomics/tradingeconomics-python, 
# analysis report https://api.simplize.vn/api/company/analysis-report/list?ticker=MSN&isWl=false&page=1&size=10
