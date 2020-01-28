# -*- coding: utf-8 -*-
#
import json
import logging
from typing import List
from functools import wraps

from flask import redirect, session, render_template, request, g, url_for
from six.moves.urllib.parse import urlencode

from flaskhello.models import User
from flaskhello.web import db

from .core import application
from .core import auth0


logger = logging.getLogger(__name__)


@application.context_processor
def inject_functions():
    return dict(is_authenticated=is_authenticated())


@application.context_processor
def inject_user_when_present():
    if not is_authenticated():
        return {"user": None}

    user = getattr(g, "user", None)
    return dict(user=user)


@application.route("/login")
def login():
    return auth0.authorize_redirect(
        redirect_uri=application.config["OAUTH2_CALLBACK_URL"],
        # audience=application.config["OAUTH2_CLIENT_AUDIENCE"],
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

    response = auth0.get("userinfo")
    if response.status_code != 200:
        args = dict(request.args)
        return render_template(
            "error.html",
            exception='failed to retrieve user info',
            args=response.json()
        )

    userinfo = response.json()
    session["user"] = userinfo
    session["oauth2_id"] = userinfo.get('sub')

    session["token"] = token
    session["access_token"] = token.get("access_token")
    session["jwt_token"] = token.get("id_token")

    user, token = db.get_user_and_token_from_userinfo(
        token=token,
        userinfo=userinfo
    )
    session["user"] = user.to_dict()
    session["token"] = token.to_dict()
    session["oauth2_id"] = user.oauth2_id
    session["access_token"] = token.access_token
    session["jwt_token"] = token.id_token

    return redirect("/dashboard")


def is_authenticated():
    auth_keys = {"user", "access_token", "jwt_token", "token"}
    return auth_keys.intersection(set(session.keys()))


def require_auth0(permissions: List[str]):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not is_authenticated():
                # Redirect to Login page here
                return redirect(url_for("login"))

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
        "client_id": application.config["OAUTH2_CLIENT_ID"],
        "returnTo": application.config["APP_URL_EXTERNAL"],
    }
    return redirect(auth0.api_base_url + "/v2/logout?" + urlencode(params))
