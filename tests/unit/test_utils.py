from flask import Response
from flaskhello.utils import json_response


def test_json_response_returns_flask_response():
    ("json_response() should set the proper header and serialize the data as json")

    # Given a dictionary with data
    data = {"foo": "bar"}

    # When I call json_response
    response = json_response(data)

    # Then it should have returned a flask response object
    response.should.be.a(Response)

    # And the headers should have a content-type
    response.headers.should.have.key("Content-Type")

    # And it should be application/json
    response.headers["Content-Type"].should.equal("application/json")

    # And the data should be serialized as json
    response.data.should.equal(b'{\n  "foo": "bar"\n}')
