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

def train_model(train_input: Input_Data, train_output: Output_Data, validate_input: Input_Data, validate_output: Output_Data):
    unique_name = np.unique(train_input.name_data)
    unique_industry = np.unique(train_input.industry_id_data)

    model = Stock_Model(config=config).get_model(unique_name, unique_industry)
    model.summary()
    # tf.keras.utils.plot_model(model, "multi_input_and_output_model.png", show_shapes=True)

    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',  # Monitor validation loss
        patience=10,         # Stop if no improvement for 10 epochs
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
    return history

def visualize(history):
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Training and Validation Loss')
    plt.show()

def main():
    print("Hello World, This stock guess system is running")
    data_set = Data_set(config=config)
    (train_input, train_output), (validate_input, validate_output), (test_input, test_output), meta_scaler = data_set.prepare_data()
    # train_input, train_output = revert_scale(train_input, train_output, meta_scaler)

    history = train_model(train_input, train_output, validate_input, validate_output)
    visualize(history)


if __name__ == '__main__':
	main()