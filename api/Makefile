run:
	python main.py

build:
	docker build -t home-value-estimator .
run-build-app: build
	docker run -d -p 8000:8000 home-value-estimator

