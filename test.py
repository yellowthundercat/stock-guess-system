# feature selection
# https://www.geeksforgeeks.org/feature-selection-in-python-with-scikit-learn/


from datetime import date

import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from attribute_finder.data_set import Data_set
from attribute_finder.type import *
from config.config import Config
from dateutil.relativedelta import relativedelta

from model.model import Stock_Model, save_model, load_model
from utils.utils import revert_scale

config = Config()


def main():
    data_set = Data_set(config=config)
    result = data_set.prepare_company_data('VCP')

if __name__ == '__main__':
	main()