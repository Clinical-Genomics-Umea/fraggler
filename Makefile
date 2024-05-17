install:
	pip install --upgrade pip
	pip install -r requirements.txt
format:
	black fraggler/*.py fraggler/*/*.py 
lint:
	pylint --disable=R,C *.py fraggler/*.py fraggler/*/*.py
clean:
	rm -rf dist/ build/ *.egg-info
build:
	python -m build
