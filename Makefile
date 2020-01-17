.PHONY: tests all unit functional run docker-image docker-push docker migrate db deploy deploy-with-helm port-forward wheels docker-base-image redeploy

DEPLOY_TIMEOUT		:= 300
BASE_TAG		:= $(shell git log -n1  --format=oneline Dockerfile.base | awk '{print $$1}')
PROD_TAG		:= $(shell git log -n1  --format=oneline Dockerfile | awk '{print $$1}')
BASE_IMAGE		:= flask-hello-base:$(BASE_TAG)
PROD_IMAGE		:= k8s-flask-hello:$(PROD_TAG)
export FLASK_DEBUG	:= 1
export VENV		?= .venv

all: dependencies tests

$(VENV):  # creates $(VENV) folder if does not exist
	python3 -mvenv $(VENV)


$(VENV)/bin/nosetests $(VENV)/bin/python $(VENV)/bin/pip: # installs latest pip
	test -e $(VENV)/bin/pip || make $(VENV)
	$(VENV)/bin/pip install -U pip setuptools
	$(VENV)/bin/pip install -r development.txt

# Runs the unit and functional tests
tests: $(VENV)/bin/nosetests  # runs all tests
	$(VENV)/bin/nosetests tests

# Install dependencies
dependencies: | $(VENV)/bin/nosetests


migrate:
	$(VENV)/bin/python application/migrate.py

# runs unit tests

unit: $(VENV)/bin/nosetests  # runs only unit tests
	$(VENV)/bin/nosetests --cover-erase tests/unit

functional: $(VENV)/bin/nosetests  # runs functional tests
	$(VENV)/bin/nosetests tests/functional

# runs the server, exposing the routes to http://localhost:5000
run: $(VENV)/bin/python
	$(VENV)/bin/python application/web.py

docker-base-image:
	figlet base image
	docker images | grep "$(BASE_IMAGE)" || docker build -f Dockerfile.base -t "gabrielfalcao/$(BASE_IMAGE)" .

docker-image: docker-base-image
	figlet production image
	docker build -f Dockerfile -t gabrielfalcao/$(PROD_IMAGE) .

docker-push:
	@docker login -p $$(echo  "a2ltazI1MDIK" | base64 -d) -u gabrielfalcao
	docker push gabrielfalcao/$(BASE_IMAGE)
	docker push gabrielfalcao/$(PROD_IMAGE)

wheels:
	mkdir -p wheels
	docker run --rm -w /python -v $$(pwd):/python -v $$(pwd)/wheels:/wheels python:3.7-alpine sh -c 'pip wheel -r development.txt'

docker: docker-image docker-push

deploy: deploy-with-helm

deploy-with-helm:
	helm template operations/helm > /dev/null
	newstore k8s stack install --set image.tag=$(PROD_TAG) --timeout $(DEPLOY_TIMEOUT) --no-update --atomic --debug operations/helm

port-forward:
	newstore kubectl port-forward "deployments/$$(newstore k8s space current)-helm-flask-hello 5000:5000"

rollback:
	-newstore k8s stack delete helm

db:
	-@2>/dev/null dropdb flask_hello || echo ''
	-@2>/dev/null dropuser flask_hello || echo 'no db user'
	-@2>/dev/null createuser flask_hello --createrole --createdb
	-@2>/dev/null createdb flask_hello
	-psql postgres << "CREATE ROLE flask_hello WITH LOGIN PASSWORD 'Wh15K3y'"
	-psql postgres << "GRANT ALL PRIVILEGES ON DATABASE flask_hello TO flask_hello;"

redeploy: rollback deploy
