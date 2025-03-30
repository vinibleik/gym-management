.PHONY: run lint lint-unsafe lint-full format

run: lint format
	@python main.py

lint:
	@ruff check --fix

lint-unsafe:
	@ruff check --fix --unsafe-fixes

lint-full:
	@ruff check --fix --output-format full

format:
	@ruff format
