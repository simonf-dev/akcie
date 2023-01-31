pylint-check:
	poetry run pylint stock_summary tests/
.PHONY: pylint-check

mypy-check:
	poetry run mypy --strict stock_summary/ tests/
.PHONY: mypy-check

tests:
	poetry run pytest tests/
.PHONY: tests

black:
	poetry run black stock_summary/ tests/
.PHONY: black

isort:
	poetry run isort stock_summary/ tests/
.PHONY: isort