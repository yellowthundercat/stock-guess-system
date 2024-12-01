from dataclasses import dataclass
from datetime import date

@dataclass
class Time_data:
    open: float
    close: float
    low: float
    high: float
    volume: int

@dataclass
class Day_data(Time_data):
    pass

@dataclass
class Week_data(Time_data):
    pass

@dataclass
class Month_data(Time_data):
    pass

@dataclass
class Quarter_data(Time_data):
    pass


@dataclass
class Company:
    name: str
    exchange: str
    industry_id: str
    industry_id_v2: str
    established_year: str
    top_1_shareholders: str
    top_2_shareholder: str
    others_shareholders_percent: float

    day_points: dict[date, Day_data]
    week_points: dict[date, Week_data]
    month_points: dict[date, Month_data]
    quarter_points: dict[date, Quarter_data]

    date_begin: int
    date_end: int

@dataclass
class Macro:
    # vnindex
    # vietnam
    # forex
    # us/china
    pass