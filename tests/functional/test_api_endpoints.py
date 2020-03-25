import json
from .helpers import web_test


# This test suite uses the python module "sure":
#
# https://sure.readthedocs.io/en/latest/api-reference.html#example-setup-a-flask-app-for-testing


@web_test
def test_index_page(context):
    ("GET on / should render an HTML page")

    # Given that I perform a GET /
    response = context.http.get("/")

    # Then check if the status was 200
    response.status_code.should.equal(200)

    # And when I check the content type is html
    response.headers.should.have.key("Content-Type")

    # Then it should be html
    response.headers["Content-Type"].should.contain("text/html")


@web_test
def test_hello_world(context):
    ("GET on /api/example should return a json containing hello world")

    # Given that I perform a GET /api/example
    response = context.http.get("/api/users")

    # When I check the response
    response.headers.should.have.key("Content-Type").being.equal("application/json")

    # And check if the status was 200
    response.status_code.should.equal(200)
