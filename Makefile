VENV = env
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip


all:
	clear
	python3 fly-in.py maps/easy/03_basic_capacity.txt

install:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) fly-in.py 

easy:
	python3 fly-in.py maps/easy/01_linear_path.txt
	python3 fly-in.py maps/easy/02_simple_fork.txt
	python3 fly-in.py maps/easy/03_basic_capacity.txt

medium:
	python3 fly-in.py maps/medium/01_dead_end_trap.txt
	python3 fly-in.py maps/medium/02_circular_loop.txt
	python3 fly-in.py maps/medium/03_priority_puzzle.txt


hard:
	python3 fly-in.py maps/hard/01_maze_nightmare.txt
	python3 fly-in.py maps/hard/02_capacity_hell.txt
	python3 fly-in.py maps/hard/03_ultimate_challenge.txt

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