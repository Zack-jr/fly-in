VENV = env
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip


all:
	clear
	python3 fly-in.py maps/easy/01_linear_path.txt

install:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) fly-in.py 

debug:
	python3 -m pdb fly_in.py 


clean:

	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache

lint:
	python3 -m flake8 . && python3 -m mypy . --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs


.PHONY = all install run debug clean lint