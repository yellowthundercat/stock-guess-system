from datetime import date, timedelta
import pandas as pd
from vnstock3 import Vnstock
import yfinance as yf

from attribute_finder.constant import INFLATION, USDVND, VIET_NAM_ID, VNINDEX, GDP_GROWTH
from attribute_finder.resources import get_company_average_volume, get_company_equity, get_company_list, load_analysis_report_online, load_company_online, load_vnstock_online, load_yahoo_finance_online
from config import config
import json
import matplotlib.pyplot as plt
import requests

# feature selection
# https://www.geeksforgeeks.org/feature-selection-in-python-with-scikit-learn/

import pandas_ta as ta


def main():
    # result = load_company_online('DSE', date_begin=date(2023, 1, 4), date_end=date(2024, 12, 7))
    # result = load_vnstock_online('DSE', date(2017,6,13), date(2017,6,13) + timedelta(days=1), '1D')
	result = load_yahoo_finance_online(symbol='GC=F', date_begin=date(2024, 9, 1), date_end=date(2024, 12, 1), interval='1d')
	result = load_yahoo_finance_online(symbol='GC=F', date_begin=date(2022, 1, 1), date_end=date(2024, 12, 1), interval='1mo')
	print(result)
	print(len(result))
	# result = get_company_equity('MSN')
	

if __name__ == '__main__':
	main()