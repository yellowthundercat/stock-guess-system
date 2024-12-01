from dataclasses import dataclass
from datetime import date
import os

@dataclass
class Config:
	data_path: str = os.path.join(os.path.dirname(__file__), '..', 'data')
	log_level: int = 0 # 0: debug, 1: info, 2: warning, 3: error
	default_begin_date: date = date(2024, 1, 1)
	default_end_date: date = date(2024, 2, 1)