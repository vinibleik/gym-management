.PHONY: run lint lint-unsafe lint-full format

run: lint format
	@python main.py

test:
	@python -m unittest

test-verbose:
	@python -m unittest -v

lint:
	@ruff check --fix

lint-unsafe:
	@ruff check --fix --unsafe-fixes

lint-full:
	@ruff check --fix --output-format full

format:
	@ruff format
