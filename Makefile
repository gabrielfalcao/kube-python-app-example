.PHONY: tests all unit functional run docker-image docker-push docker migrate db deploy deploy-with-helm port-forward wheels

export FLASK_DEBUG	:= 1

all: dependencies tests

.venv:  # creates .venv folder if does not exist
	python3 -mvenv .venv


.venv/bin/nosetests .venv/bin/python .venv/bin/pip: # installs latest pip
	test -e .venv/bin/pip || make .venv
	.venv/bin/pip install -U pip setuptools
	.venv/bin/pip install -r development.txt

# Runs the unit and functional tests
tests: .venv/bin/nosetests  # runs all tests
	.venv/bin/nosetests tests

# Install dependencies
dependencies: | .venv/bin/nosetests


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
	docker build -f Dockerfile.base -t gabrielfalcao/flask-hello-base .
	docker build -f Dockerfile -t gabrielfalcao/k8s-flask-hello .

docker-push:
	docker push gabrielfalcao/k8s-flask-hello

wheels:
	mkdir -p wheels
	docker run --rm -w /python -v $$(pwd):/python -v $$(pwd)/wheels:/wheels python:3.7-alpine sh -c 'pip wheel -r development.txt'

docker: docker-image docker-push

deploy: deploy-with-helm

deploy-with-helm:
	newstore k8s stack install --no-update --atomic --debug operations/helm

port-forward:
	newstore kubectl port-forward "deployments/$$(newstore k8s space current)-helm-flask-hello 5000:5000"

rollback:
	newstore k8s stack delete helm

db:
	-@2>/dev/null dropdb flask_hello || echo ''
	-@2>/dev/null dropuser flask_hello || echo 'no db user'
	-@2>/dev/null createuser flask_hello --createrole --createdb
	-@2>/dev/null createdb flask_hello
	-psql postgres << "CREATE ROLE flask_hello WITH LOGIN PASSWORD 'Wh15K3y'"
	-psql postgres << "GRANT ALL PRIVILEGES ON DATABASE flask_hello TO flask_hello;"
