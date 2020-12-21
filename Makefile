all: convert.py
	rm -fr dump devguide build
	python convert.py
	sphinx-build -b html . ./build
