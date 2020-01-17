export FLASK_DEBUG	:= 1

all: dependencies tests

.venv:  # creates .venv folder if does not exist
	python3 -mvenv .venv


.venv/bin/pip: # installs latest pip
	test -e .venv/bin/pip || make .venv
	.venv/bin/pip install -U pip setuptools


.venv/bin/python .venv/bin/nosetests: .venv/bin/pip  # ensures that test dependencies are installed (nose is a test runner)
	.venv/bin/pip install -r development.txt

# Runs the unit and functional tests
tests: .venv/bin/nosetests  # runs all tests
	.venv/bin/nosetests tests

# Install dependencies
dependencies: | .venv/bin/pip


migrate:
	.venv/bin/python application/migrate.py

# runs unit tests

unit: .venv/bin/nosetests  # runs only unit tests
	.venv/bin/nosetests --cover-erase tests/unit

functional: .venv/bin/nosetests  # runs functional tests
	.venv/bin/nosetests tests/functional

# runs the server, exposing the routes to http://localhost:5000
run: .venv/bin/python
	.venv/bin/python application/web.py

docker-image:
	docker build -t gabrielfalcao/k8s-flask-hello .

docker-push:
	docker push gabrielfalcao/flask-hello

docker: docker-image docker-push

.PHONY: tests all unit functional run docker-image docker-push docker migrate


db:
	-@2>/dev/null dropdb flask_hello || echo ''
	-@2>/dev/null dropuser flask_hello || echo 'no db user'
	-@2>/dev/null createuser flask_hello --createrole --createdb
	-@2>/dev/null createdb flask_hello
	-psql postgres << "CREATE ROLE flask_hello WITH LOGIN PASSWORD 'Wh15K3y'"
	-psql postgres << "GRANT ALL PRIVILEGES ON DATABASE flask_hello TO flask_hello;"
