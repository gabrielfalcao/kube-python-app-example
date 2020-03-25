.PHONY: tests all unit functional run docker-image docker-push docker migrate db deploy deploy-with-helm port-forward wheels docker-base-image redeploy check docker-pull clean

export FLASK_DEBUG	:= 1
export VENV		?= .venv
export HTTPS_API	?= $(shell ps aux | grep ngrok | grep -v grep)

# https://manage.auth0.com/dashboard/us/dev-newstore/applications/N6l4Wi2JmIh5gXiGj2sibsZiJRJu0jj1/settings
export OAUTH2_ACCESS_TOKEN_URL	:= https://id.t.newstore.net/realms/dodici/protocol/openid-connect/token
export OAUTH2_AUTHORIZE_URL	:= https://id.t.newstore.net/realms/dodici/protocol/openid-connect/auth
export OAUTH2_BASE_URL		:= https://id.t.newstore.net/realms/dodici/protocol/openid-connect/
export OAUTH2_CALLBACK_URL	:= https://newstore-keycloak-test.ngrok.io/callback/oauth2
export OAUTH2_CLIENT_ID		:= newstore-omnichannel-manager
export OAUTH2_CLIENT_SCOPE	:= openid profile email roles profile picture email_verified http://newstore/flask-test http://newstore/newstore_id
export OAUTH2_CLIENT_SECRET	:= 398796d5-71fc-41fd-9493-ded44248b2e4
export OAUTH2_DOMAIN		:= id.t.newstore.net
export OAUTH2_CLIENT_AUDIENCE	:= https://newstore-keycloak-test.ngrok.io/


DEPLOY_TIMEOUT		:= 300
BASE_TAG		:= $(shell git log --pretty="format:%h" -n1 Dockerfile.base *.txt setup.py)
PROD_TAG		:= $(shell git log --pretty="format:%h" -n1 .)
DOCKER_AUTHOR		:= gabrielfalcao
BASE_IMAGE		:= flask-hello-base
PROD_IMAGE		:= k8s-flask-hello
HELM_SET_VARS		:= --set image.tag=$(PROD_TAG) --set image.repository=$(DOCKER_AUTHOR)/$(PROD_IMAGE) --set oauth2.client_id=$(OAUTH2_CLIENT_ID) --set oauth2.client_secret=$(OAUTH2_CLIENT_SECRET)
NAMESPACE		:= $$(newstore k8s space current)
FIGLET			:= (2>/dev/null which figlet && figlet) || echo


all: dependencies tests

$(VENV):  # creates $(VENV) folder if does not exist
	python3 -mvenv $(VENV)
	$(VENV)/bin/pip install -U pip setuptools

$(VENV)/bin/flask-hello $(VENV)/bin/nosetests $(VENV)/bin/python $(VENV)/bin/pip: # installs latest pip
	test -e $(VENV)/bin/pip || make $(VENV)
	$(VENV)/bin/pip install -r development.txt
	$(VENV)/bin/pip install -e .

# Runs the unit and functional tests
tests: $(VENV)/bin/nosetests  # runs all tests
	$(VENV)/bin/nosetests tests

# Install dependencies
dependencies: | $(VENV)/bin/nosetests
	$(VENV)/bin/pip install -r development.txt

check:
	$(VENV)/bin/flask-hello check

migrate:
	$(VENV)/bin/flask-hello migrate-db

# runs unit tests

unit: $(VENV)/bin/nosetests  # runs only unit tests
	$(VENV)/bin/nosetests --cover-erase tests/unit

functional: $(VENV)/bin/nosetests  # runs functional tests
	$(VENV)/bin/nosetests tests/functional

# runs the server, exposing the routes to http://localhost:5000
run: $(VENV)/bin/python
	$(VENV)/bin/flask-hello web --port=5000


docker-base-image:
	@$(FIGLET) base image
	docker images | grep "$(BASE_IMAGE):$(BASE_TAG)" || docker build -f Dockerfile.base -t "$(DOCKER_AUTHOR)/$(BASE_IMAGE):$(BASE_TAG)" .

docker-image: docker-base-image
	$(FIGLET) production image
	docker tag "$(DOCKER_AUTHOR)/$(BASE_IMAGE):$(BASE_TAG)" "$(DOCKER_AUTHOR)/$(BASE_IMAGE)"
	docker build -f Dockerfile -t $(DOCKER_AUTHOR)/$(PROD_IMAGE):$(PROD_TAG) .
	docker tag $(DOCKER_AUTHOR)/$(PROD_IMAGE):$(PROD_TAG) $(DOCKER_AUTHOR)/$(PROD_IMAGE):latest

docker-push:
	@2>/dev/null docker login -p $$(echo  "a2ltazI1MDIK" | base64 -d) -u gabrielfalcao
	docker push $(DOCKER_AUTHOR)/$(PROD_IMAGE):$(PROD_TAG)

docker-push-all: docker-push
	docker push $(DOCKER_AUTHOR)/$(BASE_IMAGE):$(BASE_TAG)
	docker push $(DOCKER_AUTHOR)/$(BASE_IMAGE)
	docker push $(DOCKER_AUTHOR)/$(PROD_IMAGE)

wheels:
	mkdir -p wheels
	docker run --rm -w /python -v $$(pwd):/python -v $$(pwd)/wheels:/wheels python:3.7-alpine sh -c 'pip wheel -r development.txt'

docker: docker-image docker-push

docker-pull:
	docker pull $(DOCKER_AUTHOR)/$(BASE_IMAGE):$(BASE_TAG)
	docker pull $(DOCKER_AUTHOR)/$(PROD_IMAGE):$(PROD_TAG)
	docker pull $(DOCKER_AUTHOR)/$(PROD_IMAGE)

port-forward:
	newstore k8s run kubepfm --target "$(NAMESPACE):.*kibana.*:5601:5601" --target "$(NAMESPACE):.*web:5000:5000" --target "$(NAMESPACE):.*elastic.*:9200:9200" --target "$(NAMESPACE):.*elastic.*:9300:9300" --target "$(NAMESPACE):.*queue:4242:4242" --target "$(NAMESPACE):.*queue:6969:6969" --target "$(NAMESPACE):.*forwarder:5353:5353" --target "$(NAMESPACE):.*forwarder:5858:5858"

forward-queue-port:
	newstore k8s run kubepfm --target "$(NAMESPACE):.*queue:4242:4242"

db: $(VENV)/bin/flask-hello
	-@2>/dev/null dropdb flask_hello || echo ''
	-@2>/dev/null dropuser flask_hello || echo 'no db user'
	-@2>/dev/null createuser flask_hello --createrole --createdb
	-@2>/dev/null createdb flask_hello
	-@psql postgres << "CREATE ROLE flask_hello WITH LOGIN PASSWORD 'Wh15K3y'"
	-@psql postgres << "GRANT ALL PRIVILEGES ON DATABASE flask_hello TO flask_hello;"
	$(VENV)/bin/flask-hello migrate-db

deploy:
	helm template $(HELM_SET_VARS) operations/helm > /dev/null
	-(2>/dev/null newstore k8s space current && newstore k8s stack delete all) || newstore k8s space create
	make helm-install

helm-install:
	git push
	helm dependency update --skip-refresh operations/helm/
	newstore k8s helm install $(HELM_SET_VARS) -n $(PROD_TAG) --timeout $(DEPLOY_TIMEOUT) --no-update --debug operations/helm


rollback:
	helm template $(HELM_SET_VARS) operations/helm > /dev/null
	-newstore k8s space delete all --confirm

redeploy: rollback deploy

enqueue:
	$(VENV)/bin/flask-hello enqueue -x $(X) -n 10 --address='tcp://127.0.0.1:4242' "$${USER}@$$(hostname):[SENT=$$(date +'%s')]"

close:
	$(VENV)/bin/flask-hello close --address='tcp://127.0.0.1:4242'

worker:
	$(VENV)/bin/flask-hello worker --address='tcp://127.0.0.1:6969'

helm-setup:
	helm repo add elastic https://helm.elastic.co
	2>/dev/null newstore k8s space current || newstore k8s space create

tunnel:
	ngrok http --subdomain=newstore-keycloak-test 5000

clean:
	rm -rf .venv
