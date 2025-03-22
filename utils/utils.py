from datetime import date
from typing import Dict, Optional

import pandas as pd
from fake_useragent import UserAgent

from attribute_finder.type import *

def parse_hypen(date: date) -> str:
    return f"{date.year}-{date.month}-{date.day}"

def revert_data(input: Input_Data, output: Output_Data, meta_scaler: Scaler_Meta) -> tuple[Input_Data, Output_Data]:
    input.day_data = input.day_data * meta_scaler.day_data_std + meta_scaler.day_data_mean
    input.month_data = input.month_data * meta_scaler.month_data_std + meta_scaler.month_data_mean
    input.quarter_data = input.quarter_data * meta_scaler.quarter_data_std + meta_scaler.quarter_data_mean
    input.flat_data = input.flat_data * meta_scaler.flat_data_std + meta_scaler.flat_data_mean
    output.short_term_result = output.short_term_result * meta_scaler.result_std + meta_scaler.result_mean
    output.mid_term_result = output.mid_term_result * meta_scaler.result_std + meta_scaler.result_mean
    output.long_term_result = output.long_term_result * meta_scaler.result_std + meta_scaler.result_mean
    return input, output

def revert_result(output: tf.Tensor, meta_scaler: Scaler_Meta) -> np.array:
    return output * meta_scaler.result_std + meta_scaler.result_mean

# copy from vnstock3 
def as_df(history_data: Dict, interval: str, floating: Optional[int] = 2) -> pd.DataFrame:
    if not history_data:
        raise ValueError("Input data is empty or not provided.")

    # Select and rename columns directly using a dictionary comprehension
    columns_of_interest = {key: OHLC_MAP[key] for key in OHLC_MAP.keys() & history_data.keys()}
    df = pd.DataFrame(history_data)[columns_of_interest.keys()].rename(columns=OHLC_MAP)
    # rearrange columns by open, high, low, close, volume, time
    df = df[['time', 'open', 'high', 'low', 'close', 'volume']]

    # Ensure 'time' column data are numeric (integers), then convert to datetime
    df['time'] = pd.to_datetime(df['time'].astype(int), unit='s').dt.tz_localize('UTC') # Localize the original time to UTC
    # Convert UTC time to Asia/Ho_Chi_Minh timezone, make sure time is correct for minute and hour interval
    df['time'] = df['time'].dt.tz_convert('Asia/Ho_Chi_Minh')

    # round open, high, low, close to 2 decimal places
    df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].round(floating)

    # if self.resolution is not in 1m, 1H, 1D, resample the data
    if interval not in ["1m", "1H", "1D"]:
        df = df.set_index('time').resample(RESAMPLE_MAP[interval]).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).reset_index()

    # set datatype for each column using _OHLC_DTYPE
    for col, dtype in OHLC_DTYPE.items():
        if dtype == "datetime64[ns]":
            df[col] = df[col].dt.tz_localize(None)  # Remove timezone information
            if interval == "1D":
                df[col] = df[col].dt.date
        df[col] = df[col].astype(dtype)

    return df

def get_header():
    ua = UserAgent(fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')
    headers = DEFAULT_HEADERS.copy()
    # headers['User-Agent'] = ua.random
    headers['User-Agent'] = ua.chrome
    headers.update(HEADERS_MAPPING_SOURCE.get('VCI', {}))
    return headers