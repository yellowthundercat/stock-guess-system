from attribute_finder.data_set import  Data_set
from config.config import Config

class Attribute_finder:
    config: Config
    data: Data_set

    def __init__(self, config: Config, data: Data_set):
        self.config = config
        self.data = data