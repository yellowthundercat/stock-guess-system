from dataclasses import dataclass
from config.config import Config
from vnstock3 import Vnstock

DEFAULT_SOURCE = 'VCI'

stock_api = Vnstock().stock(source=DEFAULT_SOURCE)


@dataclass
class Date:
    day: int
    month: int
    year: int

    def __str__(self):
        return f"{self.year}-{self.month}-{self.day}"

@dataclass
class Stock_point:
    # General
    name: str
    date: Date

    #TA
    price: float
    lowest: float
    highest: float
    volume: int

    # FA
    PE: float
    PB: float
    EPS: float

class Attribute_finder:
    config: Config
    data: dict[tuple[Date, str], Stock_point]

    def __init__(self, config: Config):
        self.config = config

    def find_attribute(self, name: str, date: Date):
        key = (date, name)
        if key in self.data:
            return self.data[key]
        else:
            # UPDATE: load from file 
            return self.find_attribute_online(name, date)
        
    def find_attribute_online(self, name: str, date: Date):
        # UPDATE: get data from online
        data_point = stock_api.quote.history(symbol=name, start=date.__str__, end=date.__str__)
        # return Stock_point(
        #     name=name,
        #     date=date,
        #     price=stock.quote,
        #     lowest=stock.get_lowest(name),
        #     highest=stock.get_highest(name),
        #     volume=stock.get_volume(name),
        #     PE=stock.get_PE(name),
        #     PB=stock.get_PB(name),
        #     EPS=stock.get_EPS(name)
        # )