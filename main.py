from attribute_finder.attribute_finder import Attribute_finder, Date
from config.config import Config


def main():
    print("Hello World")
    config = Config()
    finder = Attribute_finder(config=config)
    finder.find_attribute_online('MSN', date=Date(29,11,2024))

if __name__ == '__main__':
	main()