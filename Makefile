.PHONY: check check-repo list-work

check: check-repo

check-repo:
	python3 scripts/check_repository.py

list-work:
	python3 scripts/list_work.py
