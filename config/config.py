from dataclasses import dataclass, field
from datetime import date
import os

@dataclass
class Config:
	# path
	model_name: str = 'stock_model_small_v1.0.1'
	data_path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
	raw_data_path: str = os.path.join(data_path, 'raw')
	preprocessed_data_path: str = os.path.join(data_path, 'preprocessed')
	model_path: str = os.path.join(data_path, 'model')

	# data
	log_level: int = 0 # 0: debug, 1: info, 2: warning, 3: error
	extend_begin_date: date = date(2020, 1, 1)
	default_begin_date: date = date(2022, 1, 1)
	default_end_date: date = date(2024, 12, 1)
	default_company_list: list = field(default_factory=lambda: ["MSN", "AGG", "FPT", "ACB", "HAG", "PTB", "NKG", "HCM", "TNG", "PVS", "VDS"]) 
	validate_rate: float = 0.15 
	test_rate: float = 0.1
	stop_lost_ratio: float = 0 # 10%, will test with 7, 19, 15, 100

	day_data_size: int = 20
	month_data_size: int = 12
	quarter_data_size: int = 8

	industry_id: str = 'v1' # v1 or v2, v2 is more detail

	name_num: int = 11 # placeholder
	industry_num: int = 10 # placeholder

	# model
	name_embedding_size: int = 4
	industry_embedding_size: int = 4
	day_lstm_size: int = 32
	month_lstm_size: int = 24
	quarter_lstm_size: int = 48
	flat_feature_size: int = 24
	default_hidden_activation: str = 'relu'
	mlp_layer: int = 2 # 2 or 3 layers
	mlp_hidden_size: int = 80
	optimizer: str = 'adam'
	optimizer_learning_rate: float = 0.0005
	loss_function: str = 'mse'
	lstm_dropout: float = 0.1
	mlp_dropout: float = 0.1

	# training
	epochs: int = 100
	batch_size: int = 256