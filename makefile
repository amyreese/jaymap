SRC := jaymap

build:
	flit build

dev:
	flit install --symlink

setup:
	python -m pip install -Ur requirements-dev.txt

.venv:
	python -m venv .venv
	source .venv/bin/activate && make setup dev
	echo 'run `source .venv/bin/activate` to use virtualenv'

venv: .venv

release: lint test clean
	flit publish

format:
	python -m usort format $(SRC)
	python -m black $(SRC)

lint:
	python -m pylint --rcfile .pylint $(SRC)
	python -m usort check $(SRC)
	python -m black --check $(SRC)

test:
	python -m coverage run -m $(SRC).tests
	python -m coverage report
	python -m mypy $(SRC)

html: .venv README.md docs/*
	source .venv/bin/activate && sphinx-build -b html docs html

clean:
	rm -rf build dist html README MANIFEST *.egg-info

distclean: clean
	rm -rf .venv