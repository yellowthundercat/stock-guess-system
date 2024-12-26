from dataclasses import dataclass, field
from datetime import date
import os

@dataclass
class Config:
	# path
	model_name: str = 'stock_model_large_v1_2flat_2_32att_160_3mlp_2drop_512batch_01learn'
	data_path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
	raw_data_path: str = os.path.join(data_path, 'raw')
	preprocessed_data_path: str = os.path.join(data_path, 'preprocessed')
	medium_data_path: str = os.path.join(data_path, 'medium')
	model_path: str = os.path.join(data_path, 'model')
	image_path: str = os.path.join(data_path, 'image')

	# data
	log_level: int = 0 # 0: debug, 1: info, 2: warning, 3: error
	extend_begin_date: date = date(2012, 1, 1)
	default_begin_date: date = date(2015, 1, 1)
	default_end_date: date = date(2024, 12, 1)
	validate_rate: float = 0.15 
	test_rate: float = 0.1
	stop_lost_ratio: float = 0 # 10%, will test with 7, 19, 15, 100

	day_data_size: int = 20
	month_data_size: int = 12
	quarter_data_size: int = 8
	industry_id: str = 'v1' # v1 or v2, v2 is more detail

	# model
	name_embedding_size: int = 4
	industry_embedding_size: int = 4

	time_layer: str = 'lstm' # lstm or attention
	num_heads: int = 2
	key_dim: int = 8
	attention_each_size: int = 8
	day_lstm_size: int = 32*2
	month_lstm_size: int = 24*2
	quarter_reduce_size: int = 24
	quarter_lstm_size: int = quarter_reduce_size*2
	flat_feature_size: int = 24*2
	default_hidden_activation: str = 'relu'
	mlp_layer: int = 3 # 2 or 3 layers
	mlp_hidden_size: int = 160
	optimizer: str = 'adam'
	optimizer_learning_rate: float = 0.0001
	optimizer_beta_1: float = 0.9
	loss_function: str = 'mse'
	dropout: float = 0.2

	# training
	override: bool = False
	epochs: int = 100
	batch_size: int = 512
	patience: int = 5