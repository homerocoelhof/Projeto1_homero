.PHONY: install run test

install:
	python -m pip install -r requirements.txt

run:
	python -m uvicorn app.main:app --reload

test:
	python -m pytest
