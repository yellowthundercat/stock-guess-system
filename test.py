import pandas as pd
from vnstock3 import Vnstock
import yfinance as yf

from attribute_finder.constant import INFLATION, USDVND, VIET_NAM_ID, VNINDEX, GDP_GROWTH
from config import config
import json

# feature selection
# https://www.geeksforgeeks.org/feature-selection-in-python-with-scikit-learn/

import pandas_ta as ta

# Create a DataFrame so 'ta' can be used.
df = pd.DataFrame()

# Help about an indicator such as bbands
help(ta.bbands)