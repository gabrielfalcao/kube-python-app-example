# -*- coding: utf-8 -*-
#
import logging
from flask_restplus import Api
from flask_restplus import Resource
from flask_restplus import fields
from flask import url_for
from .base import application

from flaskhello import config
from flaskhello.models import User
from flaskhello.worker.client import EchoClient


logger = logging.getLogger(__name__)


if config.HTTPS_API:

    # monkey-patch Flask-RESTful to generate proper swagger url
    @property
    def specs_url(self):
        """Monkey patch for HTTPS"""
        return url_for(self.endpoint("specs"), _external=True, _scheme="https")

    logger.warning(
        "monkey-patching swagger to support https " "(because HTTPS_API env var is set)"
    )
    Api.specs_url = specs_url


api = Api(application, doc="/api/")

user_json = api.model(
    "User",
    {
        "id": fields.String(required=False, description="the user id"),
        "email": fields.String(required=False, description="email address"),
        "token": fields.String(required=False, description="token"),
    },
)
rpc_request = api.model(
    "request", {"data": fields.String(required=True, description="some data")}
)

ns = api.namespace("users", description="User operations", path="/api/")


@ns.route("/user")
class UserListEndpoint(Resource):
    def get(self):
        users = User.all()
        return [u.to_dict() for u in users]

    @ns.expect(user_json)
    def post(self):
        email = api.payload.get("email")
        password = api.payload.get("password")
        try:
            user = User.create(email=email, password=password)
            return user.to_dict(), 201
        except Exception as e:
            return {"error": str(e)}, 400


@ns.route("/user/<user_id>")
class UserEndpoint(Resource):
    def get(self, user_id):
        user = User.find_one_by(id=user_id)
        if not user:
            return {"error": "user not found"}, 404

        return user.to_dict()

    def delete(self, user_id):
        user = User.find_one_by(id=user_id)
        if not user:
            return {"error": "user not found"}, 404

        user.delete()
        return {"deleted": user.to_dict()}

    @ns.expect(user_json)
    def put(self, user_id):
        user = User.find_by(id=user_id)
        if not user:
            return {"error": "user not found"}, 404

        user = user.update_and_save(**api.payload)
        return user.to_dict(), 200


@api.route("/health")
class HealthCheck(Resource):
    def get(self):
        return {"system": "ok"}


@api.route("/rpc")
class RPCRequest(Resource):
    @ns.expect(rpc_request)
    def post(self):
        data = api.payload.get("data")
        client = EchoClient()
        return client.request(data)
