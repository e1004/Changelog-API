.PHONY: pin
pin:
	# https://github.com/jazzband/pip-tools/issues/2176
	python3 -m pip install --only-binary :all: --upgrade pip-tools 'pip < 25.1' wheel setuptools
	python3 -m piptools compile --strip-extras --quiet --generate-hashes --upgrade requirements/prod.in -o requirements/prod.txt
	python3 -m piptools compile --strip-extras --quiet --generate-hashes --upgrade requirements/dev.in -o requirements/dev.txt

.PHONY: install
install:
	python3 -m pip install --only-binary :all: --upgrade pip wheel
	python3 -m pip install --only-binary :all: --require-hashes -r requirements/dev.txt -r requirements/prod.txt
	python3 -m pip check

.PHONY: test
test:
	python3 -m pip install -e .
	PROJECT_DATABASE_PATH=./database.sqlite python3 -m pytest --cov=src --cov-report=term-missing

.PHONY: lint
lint:
	python3 -m ruff check .
	python3 -m ruff format . --check
	MYPYPATH=src python3 -m mypy --namespace-packages --explicit-package-bases src test
