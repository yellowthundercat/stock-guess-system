"""
Module quản lý thông tin tỷ giá từ nguồn dữ liệu MISC.
"""

import json
import pandas as pd
from typing import Optional, List, Dict, Tuple, Union
from .const import _GRAPHQL_URL, _EXCHANGE_RATE_PERIOD_MAP, _UNIT_MAP, SUPPORTED_LANGUAGES
from vnstock.core.utils import client
from vnstock.core.utils.parser import get_asset_type, camel_to_snake
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.utils.transform import replace_in_column_names, flatten_hierarchical_index
import requests
from io import BytesIO
import base64
import datetime
import warnings

logger = get_logger(__name__)

warnings.filterwarnings("ignore", message="Workbook contains no default style, apply openpyxl's default")

def vcb_exchange_rate(date='2023-12-26'):
    """
    Get exchange rate from Vietcombank for a specific date.
    
    Parameters:
        date (str): Date in format YYYY-MM-DD. If left blank, the current date will be used.
    """
    if date == '':
        date = datetime.datetime.now().strftime('%Y-%m-%d')
    else:
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            print("Error: Incorrect date format. Should be YYYY-MM-DD.")

    url = f"https://www.vietcombank.com.vn/api/exchangerates/exportexcel?date={date}"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        excel_data = base64.b64decode(json_data["Data"])  # Decode base64 data
        columns = ['CurrencyCode', 'CurrencyName', 'Buy Cash', 'Buy Transfer', 'Sell' ]
        df = pd.read_excel(BytesIO(excel_data), sheet_name='ExchangeRate')
        df.columns = columns
        df = df.iloc[2:-4]
        df['date'] = date
        df.columns = [camel_to_snake(col) for col in df.columns]
        return df
    else:
        print(f"Error: Unable to fetch data. Details: {response.text}")