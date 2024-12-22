from datetime import date

import pandas as pd
import tensorflow as tf
from attribute_finder.data_set import Data_set
from config.config import Config
from dateutil.relativedelta import relativedelta


def main():
    print("Hello World, This stock guess system is running")
    config = Config()
    data_set = Data_set(config=config)
    result = data_set.prepare_data()
    # tensor = tf.convert_to_tensor(result)
    # print(result)
    # print(tensor.shape)


if __name__ == '__main__':
	main()