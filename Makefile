setup:
	pip install -r tests/requirements.txt

test:
	flake8 aldryn_forms --max-line-length=120 --ignore=E731 --exclude=*/migrations/*,*/south_migrations/*,*/static/*,*__init__*
	coverage erase
	coverage run --source='aldryn_forms' --omit='*migrations*' setup.py test
	coverage report
