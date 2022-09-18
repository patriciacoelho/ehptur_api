all:
	@echo "install     - Install dependencies"
	@echo "clean   - Delete generated files"
	@echo "run    - Run application"
	@echo "dev    - Run application in development mode"

clean:
	rm -rf build dist src/*.egg-info .tox .pytest_cache pip-wheel-metadata .DS_Store
	find src -name '__pycache__' | xargs rm -rf
	find tests -name '__pycache__' | xargs rm -rf

install:
	python -m pip install -e .

dev:
	FLASK_DEBUG=true FLASK_APP=api flask run --cert adhoc

run:
	FLASK_APP=api flask run

.PHONY: all install clean dev