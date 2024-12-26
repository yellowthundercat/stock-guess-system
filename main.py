from datetime import date, datetime
import os

import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from attribute_finder.data_set import Data_set
from attribute_finder.type import *
from config.config import Config
from dateutil.relativedelta import relativedelta

from model.model import Stock_Model, save_model, load_model
from utils.logger import Logger
from utils.utils import revert_data, revert_result

config = Config()
logger = Logger(config.log_level)

def train_model(train_input: Input_Data, train_output: Output_Data, validate_input: Input_Data, validate_output: Output_Data):
    logger.info("Start training model", config.model_name)
    unique_name = np.unique(train_input.name_data)
    unique_industry = np.unique(train_input.industry_id_data)

    model = Stock_Model(config=config).get_model(unique_name, unique_industry)
    model.summary()
    # tf.keras.utils.plot_model(model, "multi_input_and_output_model.png", show_shapes=True)

    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',  # Monitor validation loss
        patience=config.patience,         # Stop if no improvement for 10 epochs
        restore_best_weights=True  # Revert to the best model
    )

    history = model.fit({
        'name_input': tf.convert_to_tensor(train_input.name_data, dtype=tf.string),
        'industry_input': tf.convert_to_tensor(train_input.industry_id_data, dtype=tf.string),
        'day_input': train_input.day_data,
        'month_input': train_input.month_data,
        'quarter_input': train_input.quarter_data,
        'flat_input': train_input.flat_data
    }, {
        'short_term_output': train_output.short_term_result,
        'mid_term_output': train_output.mid_term_result,
        'long_term_output': train_output.long_term_result
    }, validation_data=({
        'name_input': tf.convert_to_tensor(validate_input.name_data, dtype=tf.string),
        'industry_input': tf.convert_to_tensor(validate_input.industry_id_data, dtype=tf.string),
        'day_input': validate_input.day_data,
        'month_input': validate_input.month_data,
        'quarter_input': validate_input.quarter_data,
        'flat_input': validate_input.flat_data
    }, {
        'short_term_output': validate_output.short_term_result,
        'mid_term_output': validate_output.mid_term_result,
        'long_term_output': validate_output.long_term_result
    }), epochs=config.epochs, batch_size=config.batch_size, callbacks=[early_stopping])
    save_model(config=config, model=model)
    return history, model

def visualize(history):
    # plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Validation Loss')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = os.path.join(config.image_path, config.model_name + timestamp + '_loss.png')
    plt.savefig(file_name)
    plt.show()

def test_model(model, test_input, test_output):
    test_loss = model.evaluate({
        'name_input': tf.convert_to_tensor(test_input.name_data, dtype=tf.string),
        'industry_input': tf.convert_to_tensor(test_input.industry_id_data, dtype=tf.string),
        'day_input': test_input.day_data,
        'month_input': test_input.month_data,
        'quarter_input': test_input.quarter_data,
        'flat_input': test_input.flat_data
    }, {
        'short_term_output': test_output.short_term_result,
        'mid_term_output': test_output.mid_term_result,
        'long_term_output': test_output.long_term_result
    }, batch_size=config.batch_size)
    logger.info("Test result", test_loss)

def visualize_test_result(model, test_input: Input_Data, test_output: Output_Data, meta_scaler: Scaler_Meta):
    result = model.predict({
        'name_input': tf.convert_to_tensor(test_input.name_data, dtype=tf.string),
        'industry_input': tf.convert_to_tensor(test_input.industry_id_data, dtype=tf.string),
        'day_input': test_input.day_data,
        'month_input': test_input.month_data,
        'quarter_input': test_input.quarter_data,
        'flat_input': test_input.flat_data
    }, batch_size=config.batch_size)
    short_term_result = revert_result(result[0], meta_scaler)
    mid_term_result = revert_result(result[1], meta_scaler)
    long_term_result = revert_result(result[2], meta_scaler)
    test_input_raw, test_output_raw = revert_data(test_input, test_output, meta_scaler)
    company_names = ['ACB', 'MSN', 'AGG', 'FPT', 'REE', 'HPG', 'VHM', 'HAG']
    for company in company_names:
        company_index = np.where(test_input_raw.name_data == company)
        plt.plot(test_output_raw.short_term_result[company_index], label='Short Term Real')
        plt.plot(short_term_result[company_index], label='Short Term Predict')
        plt.xlabel('Days')
        plt.ylabel('Price')
        plt.legend()
        plt.title(f'{company} Short Term Test Result')
        plt.show()

        plt.plot(test_output_raw.mid_term_result[company_index], label='Mid Term Real')
        plt.plot(mid_term_result[company_index], label='Mid Term Predict')
        plt.legend()
        plt.title(f'{company} Mid Term Test Result')
        plt.show()

        plt.plot(test_output_raw.long_term_result[company_index], label='Long Term Real')
        plt.plot(long_term_result[company_index], label='Long Term Predict')
        plt.legend()
        plt.title(f'{company} Long Term Test Result')
        plt.show()
        
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # file_name = os.path.join(config.image_path, config.model_name + timestamp + f'_{company}_result.png')
        # plt.savefig(file_name)
        

def main():
    print("Hello World, This stock guess system is running")
    data_set = Data_set(config=config)
    (train_input, train_output), (validate_input, validate_output), (test_input, test_output), meta_scaler = data_set.prepare_data()

    history, model = train_model(train_input, train_output, validate_input, validate_output)
    visualize(history)
    logger.info("Finish training model", config.model_name, meta_scaler.result_mean, meta_scaler.result_std)

    model = load_model(config)
    test_model(model, test_input, test_output)
    visualize_test_result(model, test_input, test_output, meta_scaler)


if __name__ == '__main__':
	main()