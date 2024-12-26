from dataclasses import dataclass
from datetime import date
import json
import os
import pickle
import random
import time

import pandas as pd

from attribute_finder import company_list
from attribute_finder.attribute_finder import get_analysis_feature, get_day_data, get_flat_data, get_month_data, get_nearest_date, get_quarter_data
from attribute_finder.pmi import PMI
from attribute_finder.resources import load_company_online, load_macro_online
from attribute_finder.type import ICompany, IMacro, Input_Data, Output_Data, Scaler_Meta
from config.config import Config
from utils.logger import Logger
import tensorflow as tf
from dateutil.relativedelta import relativedelta
from attribute_finder.constant import *
import numpy as np

from utils.utils import *


logger = Logger(Config.log_level)

class Data_set:
    config: Config
    logger: Logger

    # data
    macro: IMacro
    companies: dict[str, ICompany]
    
    # meta
    company_list: list[str]
    date_begin: date
    date_end: date
    extend_date_begin: date

    def __init__(self, config: Config):
        self.config = config

        logger.info("loading data set from file", config.raw_data_path)

        meta_file = os.path.join(config.raw_data_path, 'meta.json')
        if os.path.exists(meta_file):
            with open(meta_file, 'r') as f:
                meta = json.load(f)
                self.date_begin = date.fromisoformat(meta['date_begin'])
                self.date_end = date.fromisoformat(meta['date_end'])
                self.extend_date_begin = date.fromisoformat(meta['extend_date_begin'])
                self.company_list = meta['company_list']
        else:
            logger.warning("meta file not found, creating new one")
            self.date_begin = config.default_begin_date
            self.date_end = config.default_end_date
            self.extend_date_begin = config.extend_begin_date
            self.company_list = company_list.company_list
            print(self.company_list)
            with open(meta_file, 'w') as f:
                json.dump({
                    'date_begin': self.date_begin.isoformat(),
                    'date_end': self.date_end.isoformat(),
                    'company_list': self.company_list,
                    'extend_date_begin': self.extend_date_begin.isoformat()
                }, f)
        
        macro_file = os.path.join(config.raw_data_path, 'macro.pkl')
        if os.path.exists(macro_file):
            with open(macro_file, 'rb') as f:
                self.macro = pickle.load(f)
        else:
            logger.warning("macro file not found, creating new one")
            self.macro = load_macro_online(self.date_begin, self.date_end, self.extend_date_begin)
            with open(macro_file, 'wb') as f:
                pickle.dump(self.macro, f)

        self.companies = {} 
        for company in self.company_list:
            company_file = os.path.join(config.raw_data_path, company + '.pkl')
            if os.path.exists(company_file):
                with open(company_file, 'rb') as f:
                    self.companies[company] = pickle.load(f)
            else:
                logger.warning(f"company {company} not found in file, creating new one")
                self.companies[company] = load_company_online(company, self.date_begin, self.date_end, self.extend_date_begin)
                time.sleep(1) # avoid being banned
                with open(company_file, 'wb') as f:
                    pickle.dump(self.companies[company], f)

    def load_preprocessed_data(self) -> tuple[tuple[Input_Data, Output_Data], tuple[Input_Data, Output_Data], tuple[Input_Data, Output_Data], Scaler_Meta]:
        logger.info("loading preprocessed data")
        train_flat_data = np.load(os.path.join(self.config.preprocessed_data_path, 'train_flat_data.npy'))
        train_day_data = np.load(os.path.join(self.config.preprocessed_data_path, 'train_day_data.npy'))
        train_month_data = np.load(os.path.join(self.config.preprocessed_data_path, 'train_month_data.npy'))
        train_quarter_data = np.load(os.path.join(self.config.preprocessed_data_path, 'train_quarter_data.npy'))
        train_short_term_result = np.load(os.path.join(self.config.preprocessed_data_path, 'train_short_term_result.npy'))
        train_mid_term_result = np.load(os.path.join(self.config.preprocessed_data_path, 'train_mid_term_result.npy'))
        train_long_term_result = np.load(os.path.join(self.config.preprocessed_data_path, 'train_long_term_result.npy'))
        train_name_data = np.load(os.path.join(self.config.preprocessed_data_path, 'train_name_data.npy'))
        train_industry_id_data = np.load(os.path.join(self.config.preprocessed_data_path, 'train_industry_id_data.npy'))

        validate_flat_data = np.load(os.path.join(self.config.preprocessed_data_path, 'validate_flat_data.npy'))
        validate_day_data = np.load(os.path.join(self.config.preprocessed_data_path, 'validate_day_data.npy'))
        validate_month_data = np.load(os.path.join(self.config.preprocessed_data_path, 'validate_month_data.npy'))
        validate_quarter_data = np.load(os.path.join(self.config.preprocessed_data_path, 'validate_quarter_data.npy'))
        validate_short_term_result = np.load(os.path.join(self.config.preprocessed_data_path, 'validate_short_term_result.npy'))
        validate_mid_term_result = np.load(os.path.join(self.config.preprocessed_data_path, 'validate_mid_term_result.npy'))
        validate_long_term_result = np.load(os.path.join(self.config.preprocessed_data_path, 'validate_long_term_result.npy'))
        validate_name_data = np.load(os.path.join(self.config.preprocessed_data_path, 'validate_name_data.npy'))
        validate_industry_id_data = np.load(os.path.join(self.config.preprocessed_data_path, 'validate_industry_id_data.npy'))

        test_flat_data = np.load(os.path.join(self.config.preprocessed_data_path, 'test_flat_data.npy'))
        test_day_data = np.load(os.path.join(self.config.preprocessed_data_path, 'test_day_data.npy'))
        test_month_data = np.load(os.path.join(self.config.preprocessed_data_path, 'test_month_data.npy'))
        test_quarter_data = np.load(os.path.join(self.config.preprocessed_data_path, 'test_quarter_data.npy'))
        test_short_term_result = np.load(os.path.join(self.config.preprocessed_data_path, 'test_short_term_result.npy'))
        test_mid_term_result = np.load(os.path.join(self.config.preprocessed_data_path, 'test_mid_term_result.npy'))
        test_long_term_result = np.load(os.path.join(self.config.preprocessed_data_path, 'test_long_term_result.npy'))
        test_name_data = np.load(os.path.join(self.config.preprocessed_data_path, 'test_name_data.npy'))
        test_industry_id_data = np.load(os.path.join(self.config.preprocessed_data_path, 'test_industry_id_data.npy'))

        meta = Scaler_Meta(
            result_mean=np.load(os.path.join(self.config.preprocessed_data_path, 'meta_result_mean.npy')),
            result_std=np.load(os.path.join(self.config.preprocessed_data_path, 'meta_result_std.npy')),
            day_data_mean=np.load(os.path.join(self.config.preprocessed_data_path, 'meta_day_data_mean.npy')),
            day_data_std=np.load(os.path.join(self.config.preprocessed_data_path, 'meta_day_data_std.npy')),
            month_data_mean=np.load(os.path.join(self.config.preprocessed_data_path, 'meta_month_data_mean.npy')),
            month_data_std=np.load(os.path.join(self.config.preprocessed_data_path, 'meta_month_data_std.npy')),
            quarter_data_mean=np.load(os.path.join(self.config.preprocessed_data_path, 'meta_quarter_data_mean.npy')),
            quarter_data_std=np.load(os.path.join(self.config.preprocessed_data_path, 'meta_quarter_data_std.npy')),
            flat_data_mean=np.load(os.path.join(self.config.preprocessed_data_path, 'meta_flat_data_mean.npy')),
            flat_data_std=np.load(os.path.join(self.config.preprocessed_data_path, 'meta_flat_data_std.npy'))
        )
        return (
            (Input_Data(
                day_data=train_day_data, month_data=train_month_data, quarter_data=train_quarter_data, flat_data=train_flat_data, 
                name_data=train_name_data, industry_id_data=train_industry_id_data),
                Output_Data(short_term_result=train_short_term_result, mid_term_result=train_mid_term_result, long_term_result=train_long_term_result)),
            (Input_Data(
                day_data=validate_day_data, month_data=validate_month_data, quarter_data=validate_quarter_data, flat_data=validate_flat_data,
                name_data=validate_name_data, industry_id_data=validate_industry_id_data),
                Output_Data(short_term_result=validate_short_term_result, mid_term_result=validate_mid_term_result, long_term_result=validate_long_term_result)),
            (Input_Data(
                day_data=test_day_data, month_data=test_month_data, quarter_data=test_quarter_data, flat_data=test_flat_data,
                name_data=test_name_data, industry_id_data=test_industry_id_data),
                Output_Data(short_term_result=test_short_term_result, mid_term_result=test_mid_term_result, long_term_result=test_long_term_result)),
            meta
        )
    
    def store_preprocessed_data(self, train_input: Input_Data, train_output: Output_Data, 
                                validate_input: Input_Data, validate_output: Output_Data, 
                                test_input: Input_Data, test_output: Output_Data, meta: Scaler_Meta):
        logger.info("storing preprocessed data")
        np.save(os.path.join(self.config.preprocessed_data_path, 'train_flat_data.npy'), train_input.flat_data)
        np.save(os.path.join(self.config.preprocessed_data_path, 'train_day_data.npy'), train_input.day_data)
        np.save(os.path.join(self.config.preprocessed_data_path, 'train_month_data.npy'), train_input.month_data)
        np.save(os.path.join(self.config.preprocessed_data_path, 'train_quarter_data.npy'), train_input.quarter_data)
        np.save(os.path.join(self.config.preprocessed_data_path, 'train_short_term_result.npy'), train_output.short_term_result)
        np.save(os.path.join(self.config.preprocessed_data_path, 'train_mid_term_result.npy'), train_output.mid_term_result)
        np.save(os.path.join(self.config.preprocessed_data_path, 'train_long_term_result.npy'), train_output.long_term_result)
        np.save(os.path.join(self.config.preprocessed_data_path, 'train_name_data.npy'), train_input.name_data)
        np.save(os.path.join(self.config.preprocessed_data_path, 'train_industry_id_data.npy'), train_input.industry_id_data)

        np.save(os.path.join(self.config.preprocessed_data_path, 'validate_flat_data.npy'), validate_input.flat_data)
        np.save(os.path.join(self.config.preprocessed_data_path, 'validate_day_data.npy'), validate_input.day_data)
        np.save(os.path.join(self.config.preprocessed_data_path, 'validate_month_data.npy'), validate_input.month_data)
        np.save(os.path.join(self.config.preprocessed_data_path, 'validate_quarter_data.npy'), validate_input.quarter_data)
        np.save(os.path.join(self.config.preprocessed_data_path, 'validate_short_term_result.npy'), validate_output.short_term_result)
        np.save(os.path.join(self.config.preprocessed_data_path, 'validate_mid_term_result.npy'), validate_output.mid_term_result)
        np.save(os.path.join(self.config.preprocessed_data_path, 'validate_long_term_result.npy'), validate_output.long_term_result)
        np.save(os.path.join(self.config.preprocessed_data_path, 'validate_name_data.npy'), validate_input.name_data)
        np.save(os.path.join(self.config.preprocessed_data_path, 'validate_industry_id_data.npy'), validate_input.industry_id_data)

        np.save(os.path.join(self.config.preprocessed_data_path, 'test_flat_data.npy'), test_input.flat_data)
        np.save(os.path.join(self.config.preprocessed_data_path, 'test_day_data.npy'), test_input.day_data)
        np.save(os.path.join(self.config.preprocessed_data_path, 'test_month_data.npy'), test_input.month_data)
        np.save(os.path.join(self.config.preprocessed_data_path, 'test_quarter_data.npy'), test_input.quarter_data)
        np.save(os.path.join(self.config.preprocessed_data_path, 'test_short_term_result.npy'), test_output.short_term_result)
        np.save(os.path.join(self.config.preprocessed_data_path, 'test_mid_term_result.npy'), test_output.mid_term_result)
        np.save(os.path.join(self.config.preprocessed_data_path, 'test_long_term_result.npy'), test_output.long_term_result)
        np.save(os.path.join(self.config.preprocessed_data_path, 'test_name_data.npy'), test_input.name_data)
        np.save(os.path.join(self.config.preprocessed_data_path, 'test_industry_id_data.npy'), test_input.industry_id_data)

        np.save(os.path.join(self.config.preprocessed_data_path, 'meta_result_mean.npy'), meta.result_mean)
        np.save(os.path.join(self.config.preprocessed_data_path, 'meta_result_std.npy'), meta.result_std)
        np.save(os.path.join(self.config.preprocessed_data_path, 'meta_day_data_mean.npy'), meta.day_data_mean)
        np.save(os.path.join(self.config.preprocessed_data_path, 'meta_day_data_std.npy'), meta.day_data_std)
        np.save(os.path.join(self.config.preprocessed_data_path, 'meta_month_data_mean.npy'), meta.month_data_mean)
        np.save(os.path.join(self.config.preprocessed_data_path, 'meta_month_data_std.npy'), meta.month_data_std)
        np.save(os.path.join(self.config.preprocessed_data_path, 'meta_quarter_data_mean.npy'), meta.quarter_data_mean)
        np.save(os.path.join(self.config.preprocessed_data_path, 'meta_quarter_data_std.npy'), meta.quarter_data_std)
        np.save(os.path.join(self.config.preprocessed_data_path, 'meta_flat_data_mean.npy'), meta.flat_data_mean)
        np.save(os.path.join(self.config.preprocessed_data_path, 'meta_flat_data_std.npy'), meta.flat_data_std)

    # return train data, validate data, test data
    def prepare_data(self) -> tuple[tuple[Input_Data, Output_Data], tuple[Input_Data, Output_Data], tuple[Input_Data, Output_Data], Scaler_Meta]:
        if os.path.exists(os.path.join(self.config.preprocessed_data_path, 'train_short_term_result.npy')):
            return self.load_preprocessed_data()
        train_input = Input_Data()
        train_output = Output_Data()
        validate_input = Input_Data()
        validate_output = Output_Data()
        test_input = Input_Data()
        test_output = Output_Data()
        for company in self.company_list:
            industry_id = self.companies[company].industry_id if self.config.industry_id == 'v1' else self.companies[company].industry_id_v2
            company_input, company_output = self.prepare_company_data(company)
            if  np.any(np.isnan(company_input.day_data)):
                logger.warning(f"company {company} has nan value")
                company_input.day_data = np.nan_to_num(company_input.day_data)
            comapany_len = company_input.day_data.shape[0]
            validate_size = int(comapany_len * self.config.validate_rate)
            test_size = int(comapany_len * self.config.test_rate)
            validate_position = random.randint(0, comapany_len - validate_size - test_size + 1)
            test_position = validate_position + validate_size
            end_test_position = test_position + test_size  
            
            train_input.day_data = np.concatenate([train_input.day_data, company_input.day_data[:validate_position]], axis=0)
            train_input.month_data = np.concatenate([train_input.month_data, company_input.month_data[:validate_position]], axis=0)
            train_input.quarter_data = np.concatenate([train_input.quarter_data, company_input.quarter_data[:validate_position]], axis=0)
            train_input.flat_data = np.concatenate([train_input.flat_data, company_input.flat_data[:validate_position]], axis=0)
            train_output.short_term_result = np.concatenate([train_output.short_term_result, company_output.short_term_result[:validate_position]], axis=0)
            train_output.mid_term_result = np.concatenate([train_output.mid_term_result, company_output.mid_term_result[:validate_position]], axis=0)
            train_output.long_term_result = np.concatenate([train_output.long_term_result, company_output.long_term_result[:validate_position]], axis=0)

            validate_input.day_data = np.concatenate([validate_input.day_data, company_input.day_data[validate_position:test_position]], axis=0)
            validate_input.month_data = np.concatenate([validate_input.month_data, company_input.month_data[validate_position:test_position]], axis=0)
            validate_input.quarter_data = np.concatenate([validate_input.quarter_data, company_input.quarter_data[validate_position:test_position]], axis=0)
            validate_input.flat_data = np.concatenate([validate_input.flat_data, company_input.flat_data[validate_position:test_position]], axis=0)
            validate_output.short_term_result = np.concatenate([validate_output.short_term_result, company_output.short_term_result[validate_position:test_position]], axis=0)
            validate_output.mid_term_result = np.concatenate([validate_output.mid_term_result, company_output.mid_term_result[validate_position:test_position]], axis=0)
            validate_output.long_term_result = np.concatenate([validate_output.long_term_result, company_output.long_term_result[validate_position:test_position]], axis=0)

            test_input.day_data = np.concatenate([test_input.day_data, company_input.day_data[test_position:end_test_position]], axis=0)
            test_input.month_data = np.concatenate([test_input.month_data, company_input.month_data[test_position:end_test_position]], axis=0)
            test_input.quarter_data = np.concatenate([test_input.quarter_data, company_input.quarter_data[test_position:end_test_position]], axis=0)
            test_input.flat_data = np.concatenate([test_input.flat_data, company_input.flat_data[test_position:end_test_position]], axis=0)
            test_output.short_term_result = np.concatenate([test_output.short_term_result, company_output.short_term_result[test_position:end_test_position]], axis=0)
            test_output.mid_term_result = np.concatenate([test_output.mid_term_result, company_output.mid_term_result[test_position:end_test_position]], axis=0)
            test_output.long_term_result = np.concatenate([test_output.long_term_result, company_output.long_term_result[test_position:end_test_position]], axis=0)

            train_input.day_data = np.concatenate([train_input.day_data, company_input.day_data[end_test_position:]], axis=0)
            train_input.month_data = np.concatenate([train_input.month_data, company_input.month_data[end_test_position:]], axis=0)
            train_input.quarter_data = np.concatenate([train_input.quarter_data, company_input.quarter_data[end_test_position:]], axis=0)
            train_input.flat_data = np.concatenate([train_input.flat_data, company_input.flat_data[end_test_position:]], axis=0)
            train_output.short_term_result = np.concatenate([train_output.short_term_result, company_output.short_term_result[end_test_position:]], axis=0)
            train_output.mid_term_result = np.concatenate([train_output.mid_term_result, company_output.mid_term_result[end_test_position:]], axis=0)
            train_output.long_term_result = np.concatenate([train_output.long_term_result, company_output.long_term_result[end_test_position:]], axis=0)

            train_input.name_data = np.concatenate([train_input.name_data, np.array([company] * (comapany_len-validate_size-test_size)).astype(str)], axis=0)
            validate_input.name_data = np.concatenate([validate_input.name_data, np.array([company] * (validate_size)).astype(str)], axis=0)
            test_input.name_data = np.concatenate([test_input.name_data, np.array([company] * (test_size)).astype(str)], axis=0)
            
            train_input.industry_id_data = np.concatenate([train_input.industry_id_data, np.array([industry_id] * (comapany_len-validate_size-test_size)).astype(str)], axis=0)
            validate_input.industry_id_data = np.concatenate([validate_input.industry_id_data, np.array([industry_id] * (validate_size)).astype(str)], axis=0)
            test_input.industry_id_data = np.concatenate([test_input.industry_id_data, np.array([industry_id] * (test_size)).astype(str)], axis=0)

        # scaling
        flat_mean = np.mean(train_input.flat_data, axis=0)
        flat_std = np.std(train_input.flat_data, axis=0)
        flat_std[flat_std == 0] = 1
        train_input.flat_data = (train_input.flat_data - flat_mean) / flat_std
        validate_input.flat_data = (validate_input.flat_data - flat_mean) / flat_std
        test_input.flat_data = (test_input.flat_data - flat_mean) / flat_std
        day_mean = np.mean(train_input.day_data, axis=(0, 1))
        day_std = np.std(train_input.day_data, axis=(0, 1))
        day_std[day_std == 0] = 1
        train_input.day_data = (train_input.day_data - day_mean) / day_std
        validate_input.day_data = (validate_input.day_data - day_mean) / day_std
        test_input.day_data = (test_input.day_data - day_mean) / day_std
        month_mean = np.mean(train_input.month_data, axis=(0, 1))
        month_std = np.std(train_input.month_data, axis=(0, 1))
        month_std[month_std == 0] = 1
        train_input.month_data = (train_input.month_data - month_mean) / month_std
        validate_input.month_data = (validate_input.month_data - month_mean) / month_std
        test_input.month_data = (test_input.month_data - month_mean) / month_std
        quarter_mean = np.mean(train_input.quarter_data, axis=(0, 1))
        quarter_std = np.std(train_input.quarter_data, axis=(0, 1))
        quarter_std[quarter_std == 0] = 1
        train_input.quarter_data = (train_input.quarter_data - quarter_mean) / quarter_std
        validate_input.quarter_data = (validate_input.quarter_data - quarter_mean) / quarter_std
        test_input.quarter_data = (test_input.quarter_data - quarter_mean) / quarter_std
        # scaling output
        total_result = np.concatenate([train_output.short_term_result, train_output.mid_term_result, train_output.long_term_result])
        result_mean = np.mean(np.array(total_result))
        result_std = np.std(np.array(total_result))
        result_std = 1 if result_std == 0 else result_std
        train_output.short_term_result = (train_output.short_term_result - result_mean) / result_std
        train_output.mid_term_result = (train_output.mid_term_result - result_mean) / result_std
        train_output.long_term_result = (train_output.long_term_result - result_mean) / result_std
        meta = Scaler_Meta(
            result_mean=result_mean, result_std=result_std,
            day_data_mean=day_mean, day_data_std=day_std,
            month_data_mean=month_mean, month_data_std=month_std,
            quarter_data_mean=quarter_mean, quarter_data_std=quarter_std,
            flat_data_mean=flat_mean, flat_data_std=flat_std
        )

        logger.info("data set prepared")
        logger.info(f"train data: {train_input.day_data.shape}, {train_input.month_data.shape}, {train_input.quarter_data.shape}, {train_input.flat_data.shape}")
        logger.info(f"validate data: {validate_input.day_data.shape}, {validate_input.month_data.shape}, {validate_input.quarter_data.shape}, {validate_input.flat_data.shape}")
        logger.info(f"test data: {test_input.day_data.shape}, {test_input.month_data.shape}, {test_input.quarter_data.shape}, {test_input.flat_data.shape}")
        
        unique_name = np.unique(train_input.name_data)
        unique_industry = np.unique(train_input.industry_id_data)
        logger.info(f"unique name: {len(unique_name)}, unique industry: {len(unique_industry)}")

        self.store_preprocessed_data(train_input, train_output, validate_input, validate_output, test_input, test_output, meta)
        return (train_input, train_output), (validate_input, validate_output), (test_input, test_output), meta    
    
    def prepare_company_data(self, company: str) -> tuple[Input_Data, Output_Data]:
        file_name = os.path.join(self.config.medium_data_path, company + '.pkl')
        if os.path.exists(file_name):
            with open(file_name, 'rb') as f:
                return pickle.load(f)
        logger.info(f"preparing data for company {company}")
        company_data = self.companies[company]
        start_point = max(company_data.begin_trade_date, self.date_begin) + relativedelta(months=1)
        end_point = self.date_end - relativedelta(months=6) - relativedelta(days=5)

        # prepare output
        output_data = Output_Data(
            short_term_result=self.get_company_result(company, start_point, end_point, relativedelta(months=1)),
            mid_term_result=self.get_company_result(company, start_point, end_point, relativedelta(months=3)),
            long_term_result=self.get_company_result(company, start_point, end_point, relativedelta(months=6))
        )

        # prepare input
        company_flat_data = []
        company_day_data = []
        company_month_data = []
        company_quarter_data = []
        all_day_data = self.get_day_point_input(company, pd.Timestamp(end_point))
        all_month_data = self.get_month_point_input(company, pd.Timestamp(end_point))
        all_quarter_data = self.get_quarter_point_input(company)
        all_flat_data = self.get_flat_point_input(company)
        # quarter and flat data is already reversed
        
        reverse_date = pd.date_range(start_point, end_point)[::-1]
        for i in reverse_date:
            if i not in self.companies[company].day_points.index:
                continue
            while len(all_day_data) > 0 and i < all_day_data[0][0]:
                all_day_data = all_day_data[1:]
            temp = all_day_data[:self.config.day_data_size, 1:]
            if len(temp) < self.config.day_data_size:
                empty = np.zeros((self.config.day_data_size - len(temp), DAY_SIZE))
                temp = np.concatenate([temp, empty], axis=0)
            temp = temp[::-1]
            company_day_data.append(temp)
            while len(all_month_data) > 0 and i < all_month_data[0][0]:
                all_month_data = all_month_data[1:]
            temp = all_month_data[:self.config.month_data_size, 1:]
            if len(temp) < self.config.month_data_size:
                empty = np.zeros((self.config.month_data_size - len(temp), MONTH_SIZE))
                temp = np.concatenate([temp, empty], axis=0)
            temp = temp[::-1]
            company_month_data.append(temp)
            while len(all_quarter_data) > 0 and (i.year < all_quarter_data[0][1] or 
                                                 (i.year == all_quarter_data[0][1] and i.quarter <= all_quarter_data[0][0])):
                all_quarter_data = all_quarter_data[1:]
            temp = all_quarter_data[:self.config.quarter_data_size, 2:]
            if len(temp) < self.config.quarter_data_size:
                empty = np.zeros((self.config.quarter_data_size - len(temp), QUARTER_SIZE))
                temp = np.concatenate([temp, empty], axis=0)
            temp = temp[::-1]
            company_quarter_data.append(temp)
            while len(all_flat_data) > 0 and i.year <= all_flat_data[0][0]:
                all_flat_data = all_flat_data[1:]
            temp = [i.day, i.month, i.year] + all_flat_data[0, 1:].tolist() + get_analysis_feature(company_data, i.quarter, i.year)
            company_flat_data.append(temp)

        company_day_data.reverse()
        company_month_data.reverse()
        company_quarter_data.reverse()
        company_flat_data.reverse()
        input_data = Input_Data(
            day_data=np.nan_to_num(np.array(company_day_data)).astype(float),
            month_data=np.nan_to_num(np.array(company_month_data)).astype(float),
            quarter_data=np.nan_to_num(np.array(company_quarter_data)).astype(float),
            flat_data=np.nan_to_num(np.array(company_flat_data)).astype(float)
        )
        with open(file_name, 'wb') as f:
            pickle.dump((input_data, output_data), f)
        return (input_data, output_data)
    
    def get_flat_point_input(self, company: str) -> np.ndarray:
        flat_data = []
        company_data = self.companies[company]
        macro_data = self.macro
        for year in macro_data.vn_country.gdq_growth.keys():
            flat_data.append([year] + get_flat_data(company_data, macro_data, year))
        return np.array(flat_data)

    def get_quarter_point_input(self, company: str) -> np.ndarray:
        quarter_data = []
        company_data = self.companies[company]
        for period in company_data.finances.index:
            row = company_data.finances.loc[period]
            if type(row['quarter']) != str and type(row['quarter']) != int:
                continue
            quarter = int(row['quarter'])
            year = int(row['year'])
            quarter_data.append([quarter, year] + get_quarter_data(company_data, period))
        return np.array(quarter_data)
    
    def get_month_point_input(self, company: str, end_date: pd.Timestamp) -> np.ndarray:
        month_data = [] 
        company_data = self.companies[company]
        for price_date in company_data.month_points.index:
            if price_date > end_date:
                break
            month_data.append([price_date] + get_month_data(company_data, self.macro, price_date))
        month_data.reverse()
        return np.array(month_data)

    def get_day_point_input(self, company: str, end: pd.Timestamp) -> np.ndarray:
        company_data = self.companies[company]
        day_data = []
        for price_date in company_data.day_points.index:
            if price_date > end:
                break
            day_data.append([price_date] + get_day_data(company_data, self.macro, price_date))
        day_data.reverse()
        return np.array(day_data)

    
    def get_company_result(self, company: str, start_point: date, end_point: date, delta: relativedelta) -> np.ndarray:
        if self.config.stop_lost_ratio <= 0:
            return self.get_company_result_without_stop_lost(company, start_point, end_point, delta)
        result = []
        for i in pd.date_range(start_point, end_point):
            if i in self.companies[company].day_points.index:
                result.append(self.get_point_result(company, i, delta))
        return np.array(result)
    
    def get_company_result_without_stop_lost(self, company: str, start_point: date, end_point: date, delta: relativedelta) -> np.ndarray:
        result = []
        for i in pd.date_range(start_point, end_point):
            if i in self.companies[company].day_points.index:
                start_price = self.companies[company].day_points.loc[i, CLOSE]
                estimated_end = i + delta
                while estimated_end not in self.companies[company].day_points.index:
                    estimated_end += pd.Timedelta(days=1)
                end_price = self.companies[company].day_points.loc[estimated_end, CLOSE]
                if start_price == 0:
                    logger.warning(f"start price is 0 at {i}")
                    result.append(0)
                else:
                    result.append(end_price/start_price - 1)
        return np.array(result)

    def get_point_result(self, company: str, date: pd.Timestamp, delta: relativedelta) -> float:
        start_price = self.companies[company].day_points.loc[date, CLOSE]
        if start_price == 0:
            logger.warning(f"start price is 0 at {date}")
            return 0
        highest = start_price
        end_price = start_price
        for i in pd.date_range(date, date + delta):
            if i in self.companies[company].day_points.index:
                end_price = self.companies[company].day_points.loc[i, CLOSE]
                highest = max(highest, end_price)   
                if highest / end_price > self.config.stop_lost_ratio + 1 and self.config.stop_lost_ratio > 0:
                    return end_price/start_price - 1
        return end_price/start_price - 1

