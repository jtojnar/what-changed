.PHONY: check-types lint-syntax test

check-types:
	mypy --ignore-missing-imports src/ tests/

lint-syntax:
	black -l 99999 --check --diff src/ tests/

test:
	python3 -m unittest
