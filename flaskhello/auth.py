#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import logging
from typing import List
from functools import wraps

from flask import redirect, url_for, session
from flaskhello.core import application
from flaskhello.core import auth0
from six.moves.urllib.parse import urlencode


logger = logging.getLogger(__name__)


@application.route("/login")
def login():
    return auth0.authorize_redirect(
        redirect_uri=application.config["AUTH0_CALLBACK_URI"]
    )


@application.route("/callback/auth0")
def auth0_callback():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get("userinfo")
    userinfo = resp.json()

    # Store the user information in flask session.
    session["jwt_payload"] = userinfo
    session["profile"] = {
        "user_id": userinfo["sub"],
        "name": userinfo["name"],
        "picture": userinfo["picture"],
    }
    return redirect("/dashboard")


def require_auth0(permissions: List[str]):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "jwt_payload" not in session:
                # Redirect to Login page here
                return redirect("/")

            # TODO: check if roles match
            return f(*args, **kwargs)

        return decorated

    return wrapper


@application.route("/logout")
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {
        "returnTo": url_for("home", _external=True),
        "client_id": application.config["AUTH0_CLIENT_ID"],
    }
    return redirect(auth0.api_base_url + "/v2/logout?" + urlencode(params))
