# -*- coding: utf-8 -*-
#
import logging
from flask import render_template, session, url_for, redirect, request

from . import db
from . import backend

from .auth import application
from .auth import require_auth0
from .auth import is_authenticated


logger = logging.getLogger(__name__)


@application.route("/", methods=["GET"])
def index():
    if is_authenticated():
        return redirect(url_for("dashboard"))

    return render_template("index.html")


@application.route("/config", methods=["GET"])
def config():
    return render_template("config.html")


@application.before_request
def before_request():
    # fix ngrok issue
    if request.url.startswith('http://') and 'ngrok.io' in request.url:
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)


@application.route("/dashboard", methods=["GET"])
@require_auth0("read:user")
def dashboard():
    access_token = session.get('access_token')
    if access_token:
        try:
            user, token = db.get_user_and_token_from_access_token(access_token)
            oauth2_id = user.oauth2_id
            access_token = token.access_token
        except db.BackendError:
            session.clear()
            return redirect(url_for('logout'))
    else:
        user = session["user"]
        token = session["token"]
        access_token = session['access_token']
        oauth2_id = session['oauth2_id']

    roles = backend.get_roles_from_access_token_and_oauth2_id(
        access_token=access_token,
        oauth2_id=oauth2_id,
    )

    return render_template(
        "dashboard.html",
        user=user,
        token=token,
        roles=roles,
    )
