# -*- coding: utf-8 -*-
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
from .core import keycloak


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


@application.route("/login/auth0")
def login_auth0():
    return auth0.authorize_redirect(
        redirect_uri=application.config["OAUTH2_CALLBACK_URL"],
        audience=application.config["OAUTH2_CLIENT_AUDIENCE"] or None,
    )


@application.route("/login/keycloak")
@keycloak.require_login
def login_keycloak():
    if keycloak.user_loggedin:
        return redirect("/dashboard")

    return keycloak.redirect_to_auth_server("/finalize/keycloak")


@application.route("/callback/auth0")
def auth0_callback():

    # Handles response from token endpoint
    try:
        token = auth0.authorize_access_token()
    except Exception as e:
        return render_template(
            "error.html",
            exception="Failed to retrieve OAuth2 userinfo",
            message=str(e),
            args=dict(request.args),
        )

    response = auth0.get("userinfo")

    userinfo = response.json()
    session["user"] = userinfo
    session["oauth2_id"] = userinfo.get("sub")

    session["token"] = token
    session["access_token"] = token.get("access_token")
    session["jwt_token"] = token.get("id_token")

    user, token = db.get_user_and_token_from_userinfo(token=token, userinfo=userinfo)
    session["user"] = user.to_dict()
    session["token"] = token.to_dict()
    session["oauth2_id"] = user.oauth2_id
    session["access_token"] = token.access_token
    session["jwt_token"] = token.id_token

    return redirect("/dashboard")


def ensure_oidc_session():
    userinfo = keycloak.user_getinfo(["email", "sub", "groups"])
    token = keycloak.get_cookie_id_token()
    access_token = keycloak.get_access_token()
    token["access_token"] = access_token
    token["id_token"] = token.get("jti")
    token["token_type"] = "oidc"
    token["expires_at"] = token.get("exp")

    db_user, db_token = db.get_user_and_token_from_userinfo(
        token=token, userinfo=userinfo
    )
    session["user"] = db_user.to_dict()
    session["token"] = db_token.to_dict()
    session["access_token"] = access_token
    session["oauth2_id"] = token["id_token"]
    session["jwt_token"] = keycloak.get_cookie_id_token()


def is_authenticated():
    if keycloak.user_loggedin:
        ensure_oidc_session()

    auth_keys = {"user", "access_token", "token"}
    return auth_keys.intersection(set(session.keys()))


def require_auth0(permissions: List[str]):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not is_authenticated():
                # Redirect to Login page here
                return redirect(url_for("login_keycloak"))

            # TODO: check if roles match
            return f(*args, **kwargs)

        return decorated

    return wrapper


@application.route("/logout")
def logout():
    # Clear session stored data
    session.clear()
    keycloak.logout()
    return redirect(url_for("index"))
