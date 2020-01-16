#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import os
from flask import render_template
from application.core import application
from application.utils import json_response


@application.route("/", methods=["GET"])
def frontend():
    return render_template("index.html")


def my_backend_function():
    payload = {"hello": "world"}
    return payload


@application.route("/api/example", methods=["GET"])
def api_example_route_get():
    payload = my_backend_function()
    return json_response(payload, 200)


if __name__ == "__main__":
    application.run(
        debug=bool(os.getenv('FLASK_DEBUG')),
        host=str(os.getenv('FLASK_HOST', '0.0.0.0')),
        port=int(os.getenv('FLASK_PORT', 5000)),
    )
