install:
	pip install -r requirements.txt
delete_data:
	rm -rf ./data 
	mkdir ./data
delete_raw_data:
	rm -rf ./data/raw
	mkdir ./data/raw
delete_preprocessed_data:
	rm -rf ./data/preprocessed
	mkdir ./data/preprocessed
main:
	python main.py
full:
	make delete_data
	make main