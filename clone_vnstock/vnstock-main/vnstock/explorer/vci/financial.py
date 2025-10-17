"""
Module quản lý thông tin báo cáo tài chính từ nguồn dữ liệu VCI.
"""

import json
import pandas as pd
from typing import Optional, List, Dict, Tuple, Union
from .const import _GRAPHQL_URL, _FINANCIAL_REPORT_PERIOD_MAP, _UNIT_MAP, _ICB4_COMTYPE_CODE_MAP, SUPPORTED_LANGUAGES
from vnstock.explorer.vci import Company
from vnstock.core.utils import client
from vnstock.core.utils.parser import get_asset_type, camel_to_snake
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.utils.transform import replace_in_column_names, flatten_hierarchical_index

logger = get_logger(__name__) 