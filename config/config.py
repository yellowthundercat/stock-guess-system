from dataclasses import dataclass
from datetime import date
import os

@dataclass
class Config:
	data_path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
	raw_data_path: str = os.path.join(data_path, 'raw')
	preprocessed_data_path: str = os.path.join(data_path, 'preprocessed')
	log_level: int = 0 # 0: debug, 1: info, 2: warning, 3: error
	extend_begin_date: date = date(2020, 1, 1)
	default_begin_date: date = date(2022, 1, 1)
	default_end_date: date = date(2024, 12, 1)

	evaluation_period: int = 3 # month
	validate_rate: float = 0.15 
	test_rate: float = 0.1
	stop_lost_ratio: float = 0.1 # 10%, will test with 7, 19, 15, 100

	day_data_size: int = 20
	month_data_size: int = 12
	quarter_data_size: int = 8

	industry_id: str = 'v1' # v1 or v2, v2 is more detail