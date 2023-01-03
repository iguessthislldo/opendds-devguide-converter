all: convert.py
	rm -fr dump devguide build
	python3 convert.py
	sphinx-build -b html . ./build
