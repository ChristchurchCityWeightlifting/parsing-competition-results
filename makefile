.PHONY: irun
irun:
	pipenv run ipython -i ./src/parsing-competition-results/main.py

.PHONY: run
run: 
	pipenv run python ./src/parsing-competition-results/main.py

