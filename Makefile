linters:
	black source
	isort source
	mypy source || true
	flake8 source || true
