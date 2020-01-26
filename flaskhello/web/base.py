# -*- coding: utf-8 -*-
#
import json
import logging
from flask import render_template, session, url_for, redirect
from .auth import application
from .auth import require_auth0
from .auth import is_authenticated


logger = logging.getLogger(__name__)


@application.route("/", methods=["GET"])
def index():
    if is_authenticated():
        return redirect(url_for('dashboard'))

    return render_template("index.html")


@application.route("/dashboard", methods=["GET"])
@require_auth0('read:user')
def dashboard():
    return render_template(
        "dashboard.html",
        userinfo=session["profile"],
        userinfo_pretty=json.dumps(session["jwt_payload"], indent=4),
    )
