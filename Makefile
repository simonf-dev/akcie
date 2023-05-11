pylint-check:
	poetry run pylint --load-plugins pylint_pydantic stock_summary tests/
.PHONY: pylint-check

type-check:
	poetry run mypy --strict stock_summary/ tests/
.PHONY: type-check

tests:
	poetry run pytest tests/
.PHONY: tests

black:
	poetry run black stock_summary/ tests/
.PHONY: black

isort:
	poetry run isort stock_summary/ tests/
.PHONY: isort

build:
	poetry build
.PHONY: build