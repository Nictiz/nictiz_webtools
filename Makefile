##
# Mapping Tool API
#
# @file
# @version 0.1


deps-base:
	pip-compile app/requirements/base.in --output-file=app/requirements/base.txt

deps-prod:
	pip-compile app/requirements/prod.in --output-file=app/requirements/prod.txt

deps-dev:
	pip-compile app/requirements/dev.in --output-file=app/requirements/dev.txt

deps: deps-base deps-prod deps-dev

build: deps-dev
	pip install -r app/requirements/dev.txt

install:
	pip install -r app/requirements/dev.txt

serve:
	DJANGO_SETTINGS_MODULE=app.settings.dev python manage.py runserver 0.0.0.0:8000

test:
	pytest --ds=app.settings.test
# end
