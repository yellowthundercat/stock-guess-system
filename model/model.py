import os
import tensorflow as tf

from attribute_finder.constant import *
from config.config import Config

class Stock_Model:
    config: Config
    model: tf.keras.Model = None

    def __init__(self, config: Config):
        self.config = config

    def get_model(self, name_vocab, industry_vocab) -> tf.keras.Model:
        print('#####',len(name_vocab), len(industry_vocab))
        if self.model is not None:
            return self.model
        config = self.config
        name_input_layer = tf.keras.layers.Input(shape=(), name='name_input', dtype=tf.string)
        industry_input_layer = tf.keras.layers.Input(shape=(), name='industry_input', dtype=tf.string)
        name_encoded = tf.keras.layers.StringLookup(vocabulary=name_vocab)(name_input_layer)
        industry_encoded = tf.keras.layers.StringLookup(vocabulary=industry_vocab)(industry_input_layer)
        name_embedded = tf.keras.layers.Embedding(input_dim=len(name_vocab), output_dim=config.name_embedding_size)(name_encoded)
        industry_embedded = tf.keras.layers.Embedding(input_dim=len(industry_vocab), output_dim=config.industry_embedding_size)(industry_encoded)

        day_input_layer = tf.keras.layers.Input(shape=(config.day_data_size, DAY_SIZE), name='day_input')
        month_input_layer = tf.keras.layers.Input(shape=(config.month_data_size, MONTH_SIZE), name='month_input')
        quarter_input_layer = tf.keras.layers.Input(shape=(config.quarter_data_size, QUARTER_SIZE), name='quarter_input')
        quarter_reduce = tf.keras.layers.Dense(config.quarter_reduce_size, activation=config.default_hidden_activation)(quarter_input_layer)
        quarter_reduce = tf.keras.layers.Dropout(config.dropout)(quarter_reduce)
        flat_input_layer = tf.keras.layers.Input(shape=(FLAT_SIZE,), name='flat_input')

        day_lstm = tf.keras.layers.LSTM(config.day_lstm_size, dropout=config.dropout)(day_input_layer)
        month_lstm = tf.keras.layers.LSTM(config.month_lstm_size, dropout=config.dropout)(month_input_layer)
        quarter_lstm = tf.keras.layers.LSTM(config.quarter_lstm_size, dropout=config.dropout)(quarter_input_layer)
        day_attention = tf.keras.layers.MultiHeadAttention(num_heads=config.num_heads, key_dim=config.key_dim, 
                                                        #    output_shape=config.attention_each_size,
                                                           dropout=config.dropout)(day_input_layer, day_input_layer)
        day_attention = tf.keras.layers.Add()([day_input_layer, day_attention])
        day_attention = tf.keras.layers.LayerNormalization()(day_attention)
        month_attention = tf.keras.layers.MultiHeadAttention(num_heads=config.num_heads, key_dim=config.key_dim, 
                                                            # output_shape=config.attention_each_size,
                                                            dropout=config.dropout)(month_input_layer, month_input_layer)
        month_attention = tf.keras.layers.Add()([month_input_layer, month_attention])
        month_attention = tf.keras.layers.LayerNormalization()(month_attention)
        quarter_attention = tf.keras.layers.MultiHeadAttention(num_heads=config.num_heads, key_dim=config.key_dim, 
                                                                # output_shape=config.attention_each_size,
                                                                dropout=config.dropout)(quarter_reduce, quarter_reduce)
        quarter_attention = tf.keras.layers.Add()([quarter_reduce, quarter_attention])
        quarter_attention = tf.keras.layers.LayerNormalization()(quarter_attention)
      
        day_attention_2d = tf.keras.layers.Flatten()(day_attention)
        month_attention_2d = tf.keras.layers.Flatten()(month_attention)
        quarter_attention_2d = tf.keras.layers.Flatten()(quarter_attention)
        
        flat_feature = tf.keras.layers.Dense(config.flat_feature_size, activation=config.default_hidden_activation)(flat_input_layer)
        flat_feature = tf.keras.layers.Dropout(config.dropout)(flat_feature)

        if config.time_layer == 'lstm':
            x = tf.keras.layers.Concatenate()([
                name_embedded, 
                industry_embedded,
                day_lstm, month_lstm, quarter_lstm, flat_feature])
        elif config.time_layer == 'attention':
            x = tf.keras.layers.Concatenate()([
                name_embedded, 
                industry_embedded,
                day_attention_2d, 
                month_attention_2d, 
                quarter_attention_2d, 
                flat_feature
            ])
        else:
            return None
            # x = tf.keras.layers.Concatenate()([
            #     name_embedded, 
            #     industry_embedded,
            #     day_lstm, month_lstm, quarter_lstm, 
            #     day_attention_2d, month_attention_2d, quarter_attention_2d, 
            #     flat_feature
            # ])
        
        for _ in range(config.mlp_layer):
            x = tf.keras.layers.Dense(config.mlp_hidden_size, activation=config.default_hidden_activation)(x)
            x = tf.keras.layers.Dropout(config.dropout)(x)

        short_term_output = tf.keras.layers.Dense(1, name='short_term_output')(x)
        mid_term_output = tf.keras.layers.Dense(1, name='mid_term_output')(x)
        long_term_output = tf.keras.layers.Dense(1, name='long_term_output')(x)

        model = tf.keras.Model(inputs=[
            name_input_layer, 
            industry_input_layer, 
            day_input_layer, 
            month_input_layer, 
            quarter_input_layer, 
            flat_input_layer
            ], 
            outputs=[
                short_term_output, 
                mid_term_output, 
                long_term_output
            ])
        
        optimizer = tf.keras.optimizers.Adam(learning_rate=config.optimizer_learning_rate, beta_1=config.optimizer_beta_1)
        model.compile(optimizer=optimizer, loss=config.loss_function)
        self.model = model
        return model

def load_model(config: Config) -> tf.keras.Model:
    file_name = os.path.join(config.model_path, config.model_name + '.keras')
    return tf.keras.models.load_model(file_name)
    
def save_model(config: Config, model: tf.keras.Model):
    file_name = os.path.join(config.model_path, config.model_name + '.keras')
    model.save(file_name)