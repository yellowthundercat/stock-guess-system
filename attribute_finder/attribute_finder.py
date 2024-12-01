from dataclasses import dataclass
from config.config import Config
from vnstock3 import Vnstock


tcbs_stock_api = Vnstock().stock(symbol='MSN', source="TCBS")
vci_stock_api = Vnstock().stock(symbol='MSN', source="VCI")
microsoft_stock_api = Vnstock().stock(symbol='MSN', source="MSN")

#more data https://github.com/tradingeconomics/tradingeconomics-python, 


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
    open: float
    close: float
    low: float
    high: float
    volume: int
    # calculate rsi, ma from price

    # company
    market: str
    industry_id: str
    industry_id_v2: str
    established_year: str
    top_1_shareholders: str
    top_2_shareholder: str
    others_shareholders_percent: float

    # FA

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
        data_point = tcbs_stock_api.quote.history(symbol=name, start=str(date), end=str(date))
        print(data_point)
        company_overview = tcbs_stock_api.company.overview()
        shareholders = tcbs_stock_api.company.shareholders()
        test_data = tcbs_stock_api.company.shareholders()
        print(test_data)
        # company data

        return Stock_point(
            name=name,
            date=date,
            open=data_point.at[0, 'open'],
            close=data_point.at[0, 'close'],
            high=data_point.at[0, 'high'],
            low=data_point.at[0, 'low'],
            volume=data_point.at[0, 'volume'],
            market=company_overview.at[0, 'exchange'],
            industry_id=company_overview.at[0, 'industry_id'],
            industry_id_v2=company_overview.at[0, 'industry_id_v2'],
            established_year=company_overview.at[0, 'established_year'],
            top_1_shareholders=shareholders.at[0, 'share_holder'],
            top_2_shareholder=shareholders.at[1, 'share_holder'],
            others_shareholders_percent=shareholders.iloc[-1]['share_own_percent']
        )