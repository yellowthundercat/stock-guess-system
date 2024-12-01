from attribute_finder.attribute_finder import Attribute_finder
from attribute_finder.data_set import Data_set
from config.config import Config



def main():
    print("Hello World, This stock guess system is running")
    config = Config()
    data_set = Data_set(config=config)
    finder = Attribute_finder(config=config, data=data_set)


if __name__ == '__main__':
	main()