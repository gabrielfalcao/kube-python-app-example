# -*- coding: utf-8 -*-
import jwt
import json
import logging
from typing import List
from functools import wraps

from flask import redirect, session, render_template, request, g, url_for

from flaskhello.models import JWTToken
from flaskhello.web import db

from .core import application
from .core import oauth2


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


@application.route("/login/oauth2")
def login_oauth2():
    return oauth2.authorize_redirect(
        redirect_uri=application.config["OAUTH2_CALLBACK_URL"],
        audience=application.config["OAUTH2_CLIENT_AUDIENCE"] or None,
    )


@application.route("/callback/oauth2")
def oauth2_callback():

    # Handles response from token endpoint
    try:
        token = oauth2.authorize_access_token()
    except Exception as e:
        return render_template(
            "error.html",
            exception="Failed to retrieve OAuth2 userinfo",
            message=str(e),
            args=dict(request.args),
        )

    response = oauth2.get("userinfo")

    userinfo = response.json()

    encoded_jwt_token = token.get("access_token")
    encoded_id_token = token.get("id_token")
    jwt_token = jwt.decode(encoded_jwt_token, verify=False)
    id_token = jwt.decode(encoded_id_token, verify=False)

    session["oauth2_id"] = userinfo.get("sub")
    userinfo["jwt_token"] = jwt_token
    session["token"] = token
    session["access_token"] = encoded_jwt_token
    session["id_token"] = id_token
    session["jwt_token"] = jwt_token

    user, token = db.get_user_and_token_from_userinfo(
        token=token,
        userinfo=userinfo,
    )
    session["user"] = user.to_dict()
    session["token"] = token.to_dict()

    return redirect("/dashboard")


def is_authenticated():
    auth_keys = {"user", "access_token", "token", "id_token", "jwt_token"}
    return auth_keys.intersection(set(session.keys()))


def require_oauth2(permissions: List[str]):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not is_authenticated():
                # Redirect to Login page here
                return redirect(url_for("login_oauth2"))

            # TODO: check if roles match
            return f(*args, **kwargs)

        return decorated

    return wrapper


@application.route("/logout")
def logout():
    # Clear session stored data
    session.clear()
    return redirect(request.args.get('next') or url_for("index"))
