from dataclasses import dataclass, field
from datetime import date

import numpy as np
from pandas import DataFrame
import tensorflow as tf

@dataclass
class IDeal:
    deal_announce_date: date 
    deal_action: str  
    deal_quantity: int  
    deal_price: float

@dataclass
class IAnalysis_Report:
    source: str
    issueDate: str
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
    # top_1_shareholders: str
    # top_2_shareholder: str
    others_shareholders_percent: float

    day_points: DataFrame 
    # basic 'Open', 'High', 'Low', 'Close', 'Volume'
    # ta 'SMA_50', 'SMA_200', 'BBL_20_2.0', 'BBM_20_2.0', 'BBU_20_2.0', 'BBB_20_2.0', 'BBP_20_2.0', 'RSI_14', 'SMA_20', 'STOCHk_14_3_3', 'STOCHd_14_3_3'
    month_points: DataFrame

    insider_deals: list[IDeal]
    finances: DataFrame # 78 columns
    analysis_reports: dict[tuple[str, str], IAnalysis_Report] # date, source


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
    dxy_day: DataFrame
    dxy_month: DataFrame

    dowjones_day: DataFrame
    sp500_day: DataFrame
    shanghai_day: DataFrame
    hang_seng_day: DataFrame
    nikkei_day: DataFrame
    kospi_day: DataFrame
    btc_day: DataFrame

@dataclass
class Input_Data:
    # trial: 2022-01-01 -> 2024-12-01 - 7 month -> 2.5 years -> 500 points -> 25% = 125 points, around 6 months
    # real: 2018-01-01 -> 2024-12-01 - 7 month -> 6.5 years -> 1300 points -> 25% = 325 points, around 16 months
    day_data: np.ndarray = np.empty((0, 20, 29)) # 1 month
    month_data: np.ndarray = np.empty((0, 12, 13)) # 1 years
    quarter_data: np.ndarray = np.empty((0, 8, 51)) # 2 years
    flat_data: np.ndarray = np.empty((0, 17)) 
    # need embedding 
    name_data: np.ndarray = np.array([]) # size (None)
    industry_id_data: np.ndarray = np.array([]) # size (None)


@dataclass
class Output_Data:
    # size (None, 1)
    short_term_result: np.ndarray = np.array([]) # 1 month
    mid_term_result: np.ndarray = np.array([]) # 3 months
    long_term_result: np.ndarray = np.array([]) # 6 months

@dataclass
class Scaler_Meta:
    # mean, std
    result_mean: np.ndarray
    result_std: np.ndarray
    day_data_mean: np.ndarray
    day_data_std: np.ndarray
    month_data_mean: np.ndarray
    month_data_std: np.ndarray
    quarter_data_mean: np.ndarray
    quarter_data_std: np.ndarray
    flat_data_mean: np.ndarray
    flat_data_std: np.ndarray