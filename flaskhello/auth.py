# -*- coding: utf-8 -*-
#
import json
import logging
from typing import List
from functools import wraps

from flask import redirect, url_for, session, render_template, request
from flaskhello.core import application
from flaskhello.core import auth0
from six.moves.urllib.parse import urlencode


logger = logging.getLogger(__name__)


@application.route("/login")
def login():
    return auth0.authorize_redirect(
        redirect_uri=application.config["OAUTH2_CALLBACK_URL"]
    )


@application.route("/callback/auth0")
def auth0_callback():

    # Handles response from token endpoint
    try:
        token = auth0.authorize_access_token()
    except Exception as e:
        args = dict(request.args)
        return render_template(
            "error.html", exception=e, args=json.dumps(args, indent=4)
        )

    resp = auth0.get("userinfo")
    userinfo = resp.json()
    import ipdb;ipdb.set_trace()
    # Store the user information in flask session.
    session["jwt_payload"] = userinfo
    session["token"] = token
    session["profile"] = {
        "token": token,
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
    params = {"client_id": application.config["OAUTH2_CLIENT_ID"]}
    return redirect(auth0.api_base_url + "/v2/logout?" + urlencode(params))
