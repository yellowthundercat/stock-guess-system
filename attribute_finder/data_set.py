from dataclasses import dataclass
from datetime import date
import json
import os
import pickle

from attribute_finder.resources import load_company_online, load_macro_online
from attribute_finder.type import ICompany, IDay_data, IMacro, IMonth_data, IWeek_data
from config.config import Config
from utils.logger import Logger



class Day_data(IDay_data):
    pass

class Week_data(IWeek_data):
    pass

class Month_data(IMonth_data):
    pass

class Company(ICompany):
    pass

class Macro(IMacro):
    pass

class Data_set:
    config: Config
    logger: Logger

    # data
    macro: Macro
    companies: dict[str, Company]
    
    # meta
    company_list: list[str]
    date_begin: date
    date_end: date

    def __init__(self, config: Config):
        self.config = config
        self.logger = Logger(config.log_level)

        self.logger.info("loading data set from file", config.data_path)

        meta_file = os.path.join(config.data_path, 'meta.json')
        if os.path.exists(meta_file):
            with open(meta_file, 'r') as f:
                meta = json.load(f)
                self.date_begin = date.fromisoformat(meta['date_begin'])
                self.date_end = date.fromisoformat(meta['date_end'])
                self.company_list = meta['company_list']
        else:
            self.logger.warning("meta file not found, creating new one")
            self.date_begin = config.default_begin_date
            self.date_end = config.default_end_date
            self.company_list = ['MSN']
            with open(meta_file, 'w') as f:
                json.dump({
                    'date_begin': self.date_begin.isoformat(),
                    'date_end': self.date_end.isoformat(),
                    'company_list': self.company_list
                }, f)
        
        macro_file = os.path.join(config.data_path, 'macro.pkl')
        if os.path.exists(macro_file):
            with open(macro_file, 'rb') as f:
                self.macro = pickle.load(f)
        else:
            self.logger.warning("macro file not found, creating new one")
            self.macro = load_macro_online(self.date_begin, self.date_end)
            with open(macro_file, 'wb') as f:
                pickle.dump(self.macro, f)

        self.companies = {} 
        for company in self.company_list:
            company_file = os.path.join(config.data_path, company + '.pkl')
            if os.path.exists(company_file):
                with open(company_file, 'rb') as f:
                    self.companies[company] = pickle.load(f)
            else:
                self.logger.warning(f"company {company} not found in file, creating new one")
                self.companies[company] = load_company_online(company, self.date_begin, self.date_end)
                with open(company_file, 'wb') as f:
                    pickle.dump(self.companies[company], f)
