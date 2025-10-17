"""
Module quản lý thông tin giao dịch từ nguồn dữ liệu TCBS.
"""

import json
import pandas as pd
from typing import Optional, List, Dict, Tuple, Union
from .const import _GRAPHQL_URL, _TRADING_PERIOD_MAP, _UNIT_MAP, _ICB4_COMTYPE_CODE_MAP, SUPPORTED_LANGUAGES
from vnstock.explorer.tcbs import Company
from vnstock.core.utils import client
from vnstock.core.utils.parser import get_asset_type, camel_to_snake
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.utils.transform import replace_in_column_names, flatten_hierarchical_index
from vnai import optimize_execution
from .const import _BASE_URL, _STOCKS_URL, _PRICE_BOARD_COLS_MAP, _PRICE_BOARD_STD_COLS, _PRICE_BOARD_EXT_COLS

logger = get_logger(__name__)


class Trading:
    """
    Truy xuất dữ liệu giao dịch của mã chứng khoán từ nguồn dữ liệu TCBS.
    
    Tham số:
        - symbol (str): Mã chứng khoán mặc định.
        - random_agent (bool): Sử dụng user-agent ngẫu nhiên hoặc không. Mặc định là False.
        - show_log (bool): Hiển thị thông tin log hoặc không. Mặc định là True.
    """
    def __init__(self, symbol: Optional[str], random_agent: bool = False, 
                 show_log: Optional[bool] = True):
        """
        Khởi tạo đối tượng Trading với các tham số cho việc truy xuất dữ liệu.
        """
        self.symbol = symbol.upper()
        self.asset_type = get_asset_type(self.symbol)
        self.show_log = show_log
        self.base_url = _BASE_URL
        self.headers = get_headers(data_source='TCBS', random_agent=random_agent)

        if not show_log:
            logger.setLevel('CRITICAL')
        
    # # @optimize_execution("TCBS")
    def price_board(self, symbol_ls: List[str], std_columns: Optional[bool] = True, 
                    to_df: Optional[bool] = True, show_log: bool = False) -> Union[pd.DataFrame, str]:
        """
        Truy xuất thông tin bảng giá của các mã chứng khoán tuỳ chọn từ nguồn dữ liệu TCBS.
        
        Tham số:
            - symbol_ls (List[str]): Danh sách các mã chứng khoán cần truy xuất thông tin.
            - std_columns (bool): Sử dụng danh sách cột tiêu chuẩn hoặc mở rộng. Mặc định là True.
            - to_df (bool): Chuyển đổi kết quả thành DataFrame hoặc không. Mặc định là True.
            - show_log (bool): Hiển thị thông tin log hoặc không. Mặc định là False.
            
        Returns:
            Thông tin bảng giá dưới dạng DataFrame hoặc chuỗi JSON tùy theo tham số to_df.
        """
        symbols = ",".join(symbol_ls)
        url = f'{self.base_url}/{_STOCKS_URL}/v1/stock/second-tc-price'
        
        # Use centralized API client instead of direct requests
        try:
            response_data = client.send_request(
                url=url,
                headers=self.headers,
                method="GET",
                params={"tickers": symbols},
                show_log=show_log
            )
            
            # Process response data
            data = response_data['data']
            df = pd.DataFrame(data)
            
            # Drop columns named seq
            df.drop(columns=['seq'], inplace=True, errors='ignore')
            
            # Select columns based on the std_columns parameter
            if std_columns:
                df = df[_PRICE_BOARD_STD_COLS]
            else:
                df = df[_PRICE_BOARD_EXT_COLS]

            # Rename columns according to the mapping
            df = df.rename(columns=_PRICE_BOARD_COLS_MAP)
            
            # Add source metadata
            df.source = 'TCBS'

            # Return in requested format
            if to_df:
                return df
            else:
                return df.to_json(orient='records')
                
        except Exception as e:
            # Better error handling with logging
            logger.error(f"Error processing price board data: {e}")
            return pd.DataFrame() if to_df else "[]"
