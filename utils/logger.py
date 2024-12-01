# log level
from datetime import datetime


DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3

class Logger:
    def __init__(self, level: int):
        self.level = level

    def log_time(self):
        current_time = datetime.now().time()
        print(current_time, end=" ")

    def debug(self, *values: object):
        if self.level <= DEBUG:
            self.log_time()
            print("[DEBUG]:", *values)

    def info(self, *values: object):
        if self.level <= INFO:
            self.log_time()
            print("[INFO]:", *values)
    
    def warning(self, *values: object):
        if self.level <= WARNING:
            self.log_time()
            print("[WARNING]:", *values)
    
    def error(self, *values: object):
        if self.level <= ERROR:
            self.log_time()
            print("[ERROR]:", *values)
