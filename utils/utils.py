from datetime import date

def parse_hypen(date: date) -> str:
    return f"{date.year}-{date.month}-{date.day}"