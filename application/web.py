#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import logging
import time
import os
from flask import render_template
from flask_restplus import Api
from flask_restplus import Resource
from flask_restplus import fields
from application.core import application

from application.models import User, metadata, engine


logging.getLogger().setLevel(logging.DEBUG)


@application.route("/", methods=["GET"])
def frontend():
    return render_template("index.html")


api = Api(application, doc="/api/")

user_json = api.model('User', {
    'uuid': fields.String(required=False, description="the user uuid"),
    'email': fields.String(required=False, description="email address"),
    'password': fields.String(required=False, description="password"),
})

ns = api.namespace('users', description='User operations', path='/api/')


def connect_db():
    print('trying to crate tables')
    try:
        metadata.create_all(engine)
        return True
    except Exception as e:
        print(f'failed to connect to db: {e}')
        return False


@ns.route('/user')
class UserListEndpoint(Resource):
    def get(self):
        users = User.all()
        return [u.to_dict() for u in users]

    @ns.expect(user_json)
    def post(self):
        email = api.payload.get('email')
        password = api.payload.get('password')
        try:
            user = User.create(email=email, password=password)
            return user.to_dict(), 201
        except Exception as e:
            return {'error': str(e)}, 400


@ns.route('/user/<user_id>')
class UserEndpoint(Resource):
    def get(self, user_id):
        user = User.find_one_by(id=user_id)
        if not user:
            return {'error': 'user not found'}, 404

        return user.to_dict()

    @ns.expect(user_json)
    def put(self, user_id):
        user = User.find_by(id=user_id)
        if not user:
            return {'error': 'user not found'}, 404

        user = user.update_and_save(**api.payload)
        return user.to_dict(), 200


@api.route('/health')
class HealthCheck(Resource):
    def get(self):
        try_connect_db()
        return {'system': 'ok'}


if __name__ == "__main__":
    connect_db()
    application.run(
        debug=bool(os.getenv('FLASK_DEBUG')),
        host=str(os.getenv('FLASK_HOST', '0.0.0.0')),
        port=int(os.getenv('FLASK_PORT', 5000)),
    )
