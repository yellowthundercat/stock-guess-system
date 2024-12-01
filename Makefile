install:
	pip install -r requirements.txt
delete_data:
	rm -rf ./data 
	mkdir ./data
main:
	python main.py
full:
	make delete_data
	make main