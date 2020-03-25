# -*- coding: utf-8 -*-
import jwt
import json
import logging
from typing import List
from functools import wraps

from flask import redirect, session, render_template, request, g, url_for, jsonify

from flaskhello.models import User, UserToken, JWTToken
from flaskhello.web import db

from .core import application
from .core import oauth2
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


@application.route("/delete-users")
def delete_users():
    response = {
        'users': [],
        'tokens': [],
    }
    for user in User.all():
        user.delete()
        response['users'].append(user.to_dict())

    for token in UserToken.all():
        token.delete()
        response['tokens'].append(token.to_dict())

    return jsonify(response)


@application.route("/login/oauth2")
def login_oauth2():
    return oauth2.authorize_redirect(
        redirect_uri=application.config["OAUTH2_CALLBACK_URL"],
        audience=application.config["OAUTH2_CLIENT_AUDIENCE"] or None,
    )


@application.route("/login/oidc")
@keycloak.require_login
def login_keycloak():
    if keycloak.user_loggedin:
        return redirect('/dashboard')

    return keycloak.redirect_to_auth_server('/finalize/keycloak')


@application.route("/callback/oauth2")
def oauth2_callback():

    # Handles response from token endpoint
    try:
        token = oauth2.authorize_access_token()
    except Exception as e:
        return render_template(
            "error.html",
            exception='Failed to retrieve OAuth2 userinfo',
            message=str(e),
            args=dict(request.args)
        )

    response = oauth2.get("userinfo")

    userinfo = response.json()
    session["user"] = userinfo
    session["oauth2_id"] = userinfo.get('sub')

    encoded_jwt_token = token.get("access_token")
    jwt_token = jwt.decode(encoded_jwt_token, verify=False)
    userinfo['jwt_token'] = jwt_token
    session["token"] = token
    session["access_token"] = encoded_jwt_token
    session["id_token"] = token.get("id_token")
    session["jwt_token"] = jwt_token

    user, token = db.get_user_and_token_from_userinfo(
        token=token,
        userinfo=userinfo
    )
    JWTToken.get_or_create(
        user_id=user.id,
        data=json.dumps(jwt_token),
    )
    session["user"] = user.to_dict()
    session["token"] = token.to_dict()

    return redirect("/dashboard")


def ensure_oidc_session():
    userinfo = keycloak.user_getinfo(['email', 'sub', 'groups'])
    token = keycloak.get_cookie_id_token()
    access_token = keycloak.get_access_token()
    token['access_token'] = access_token
    token['id_token'] = token.get('jti')
    token['token_type'] = 'oidc'
    token['expires_at'] = token.get('exp')

    db_user, db_token = db.get_user_and_token_from_userinfo(
        token=token,
        userinfo=userinfo
    )
    session["user"] = db_user.to_dict()
    session["token"] = db_token.to_dict()
    session['access_token'] = access_token
    session['oauth2_id'] = token['id_token']
    session['jwt_token'] = keycloak.get_cookie_id_token()


def is_authenticated():
    if keycloak.user_loggedin:
        ensure_oidc_session()

    auth_keys = {"user", "access_token", "token", "jwt_token"}
    return auth_keys.intersection(set(session.keys()))


def require_oauth2(permissions: List[str]):
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
