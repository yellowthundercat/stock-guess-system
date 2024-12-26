

import pandas as pd
from attribute_finder.constant import *
from attribute_finder.pmi import PMI
from attribute_finder.type import *
from dateutil.relativedelta import relativedelta

PMI_df = pd.DataFrame(PMI)
PMI_df["release_date"] = pd.to_datetime(PMI_df["release_date"])
PMI_df.set_index("release_date", inplace=True)

def get_analysis_feature(company_data: ICompany, quarter: int, year: int) -> list:
    recommended_price, sell, buy = 0, 0, 0
    for date_str, source in company_data.analysis_reports.keys():
        date = pd.Timestamp(date_str)
        if date.year == year and date.month in range(quarter * 3 - 2, quarter * 3 + 1):
            if company_data.analysis_reports[(date_str, source)].recommend == "MUA":
                buy += 1
            else:
                sell += 1
            recommended_price += company_data.analysis_reports[(date_str, source)].targetPrice
    return [recommended_price/(sell+buy), sell, buy] if sell+buy != 0 else [0, 0, 0]

def get_quarter_data(company_data: ICompany, period: str) -> list:
    row = company_data.finances.loc[period]
    quarter = int(row['quarter'])
    year = int(row['year'])
    quarter_data = row.drop(['quarter', 'year']).tolist()
    total_amount = 0
    for deal in company_data.insider_deals:
        if deal.deal_announce_date.year == year and deal.deal_announce_date.month in range(quarter * 3 - 2, quarter * 3 + 1):
            total_amount += deal.deal_quantity
    quarter_data += [total_amount]
    quarter_data += get_analysis_feature(company_data, quarter, year)
    return quarter_data
    
def get_flat_data(company_data: ICompany, macro_data: IMacro, year: int) -> list:
    flat_data = [
        # country
        macro_data.vn_country.gdq_growth.get(year, 0),
        macro_data.vn_country.real_interest_rate.get(year, 0),
        macro_data.vn_country.unemployment_rate.get(year, 0),
        macro_data.vn_country.inflation.get(year, 0),
        macro_data.vn_country.current_account_balance.get(year, 0),
        macro_data.vn_country.government_debt.get(year, 0),

        macro_data.us_country.real_interest_rate.get(year, 0),
        macro_data.us_country.inflation.get(year, 0),

        macro_data.china_country.real_interest_rate.get(year, 0),
        macro_data.china_country.inflation.get(year, 0),

        macro_data.vn_country.gdq_growth.get(year - 1, 0),
        macro_data.vn_country.real_interest_rate.get(year - 1, 0),
        macro_data.vn_country.inflation.get(year - 1, 0),

        # company
        company_data.others_shareholders_percent,
    ]  
    for i in range(len(flat_data)):
        if type(flat_data[i]) != int and type(flat_data[i]) != float:
            flat_data[i] = 0
    return flat_data

def get_day_data(company_data: ICompany, macro_data: IMacro, date: pd.Timestamp) -> list:
    global_date = get_nearest_date(macro_data.vnindex.day_points.index, date)
    return [
        # company
        company_data.day_points.loc[date, OPEN],
        company_data.day_points.loc[date, HIGH],
        company_data.day_points.loc[date, LOW],
        company_data.day_points.loc[date, CLOSE],
        company_data.day_points.loc[date, VOLUME],
        company_data.day_points.loc[date, SMA_50],
        company_data.day_points.loc[date, SMA_200],
        company_data.day_points.loc[date, VOL_SMA_20],
        company_data.day_points.loc[date, BBL],
        company_data.day_points.loc[date, BBM],
        company_data.day_points.loc[date, BBU],
        company_data.day_points.loc[date, RSI],
        company_data.day_points.loc[date, STOCHD],
        company_data.day_points.loc[date, STOCHK],

        # macro
        macro_data.vnindex.day_points.loc[date, CLOSE] if date in macro_data.vnindex.day_points.index else 0,
        macro_data.vnindex.day_points.loc[date, VOLUME] if date in macro_data.vnindex.day_points.index else 0,
        macro_data.vnindex.day_points.loc[date, SMA_200] if date in macro_data.vnindex.day_points.index else 0,
        macro_data.usd_day.loc[date, CLOSE] if date in macro_data.usd_day.index else 0,
        macro_data.cny_day.loc[date, CLOSE] if date in macro_data.cny_day.index else 0,
        macro_data.gold_day.loc[global_date, CLOSE] if global_date in macro_data.gold_day.index else 0,
        macro_data.oil_day.loc[global_date, CLOSE] if global_date in macro_data.oil_day.index else 0,
        macro_data.dxy_day.loc[global_date, CLOSE] if global_date in macro_data.dxy_day.index else 0,
        macro_data.sp500_day.loc[global_date, CLOSE] if global_date in macro_data.sp500_day.index else 0,
        macro_data.dowjones_day.loc[global_date, CLOSE] if global_date in macro_data.dowjones_day.index else 0,
        macro_data.shanghai_day.loc[global_date, CLOSE] if global_date in macro_data.shanghai_day.index else 0,
        macro_data.hang_seng_day.loc[global_date, CLOSE] if global_date in macro_data.hang_seng_day.index else 0,
        macro_data.nikkei_day.loc[global_date, CLOSE] if global_date in macro_data.nikkei_day.index else 0,
        macro_data.kospi_day.loc[global_date, CLOSE] if global_date in macro_data.kospi_day.index else 0,
        macro_data.btc_day.loc[global_date, CLOSE] if global_date in macro_data.btc_day.index else 0,
    ]

def get_month_data(company_data: ICompany, macro_data: IMacro, date: pd.Timestamp) -> list:
    forex_date = get_nearest_date(macro_data.usd_month.index, date)
    global_date = get_nearest_date(macro_data.gold_month.index, date)
    PMI_date = get_nearest_date(PMI_df.index, date)
    vnindex_date = get_nearest_date(macro_data.vnindex.month_points.index, date)
    month_data = [
        # company
        company_data.month_points.loc[date, OPEN],
        company_data.month_points.loc[date, HIGH],
        company_data.month_points.loc[date, LOW],
        company_data.month_points.loc[date, CLOSE],
        company_data.month_points.loc[date, VOLUME],

        # macro
        macro_data.vnindex.month_points.loc[vnindex_date, CLOSE],
        macro_data.vnindex.month_points.loc[vnindex_date, VOLUME],

        macro_data.gold_month.loc[global_date, CLOSE],
        macro_data.oil_month.loc[global_date, CLOSE],
        macro_data.dxy_month.loc[global_date, CLOSE],
    ]
    if abs(PMI_date - date) < pd.Timedelta(days=5):
        month_data += [PMI_df.loc[PMI_date, 'actual']]
    else:
        month_data += [0]
    if abs(forex_date - date) < pd.Timedelta(days=5):
        month_data += [
            macro_data.usd_month.loc[forex_date, CLOSE],
            macro_data.cny_month.loc[forex_date, CLOSE],
        ]
    else:
        month_data += [0, 0]
    return month_data

def get_nearest_date(date_list, date):
    return min(date_list, key=lambda x: abs(x.tz_localize(None) - date))