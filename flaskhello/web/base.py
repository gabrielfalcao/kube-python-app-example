# -*- coding: utf-8 -*-
#
import logging
from flask import render_template, session, url_for, redirect
from . import db
from . import backend
from flaskhello.models import User
from .auth import application
from .auth import require_oauth2
from .auth import is_authenticated


logger = logging.getLogger(__name__)


@application.route("/", methods=["GET"])
def index():
    if is_authenticated():
        return redirect(url_for("dashboard"))

    return render_template("index.html")


@application.route("/config", methods=["GET"])
def show_config():
    return render_template("config.html")


# @application.before_request
# def before_request():
#     # fix ngrok issue
#     if request.url.startswith('http://') and 'ngrok.io' in request.url:
#         return redirect(config.APP_URL_EXTERNAL, code=301)


@application.route("/dashboard", methods=["GET"])
@require_oauth2("read:user")
def dashboard():
    access_token = session.get("access_token")
    if access_token:
        try:
            user, token = db.get_user_and_token_from_access_token(access_token)
            oauth2_id = user.oauth2_id
            access_token = token.access_token
        except db.BackendError:
            session.clear()
            return redirect(url_for("logout"))
    else:
        user = session["user"]
        token = session["token"]
        access_token = session["access_token"]
        oauth2_id = session["oauth2_id"]

    roles = backend.get_roles_from_access_token_and_oauth2_id(
        access_token=access_token, oauth2_id=oauth2_id
    )

    return render_template("dashboard.html", user=user, token=token, roles=roles)


@application.route("/.reboot")
@require_oauth2("admin:system")
def reboot_process_gracefully():
    logger.critical("application container will exit gracefully because a request to /.reboot was made")
    raise SystemExit(0)


@application.route("/delete-users")
@require_oauth2("delete:user")
def delete_users():
    for user in User.all():
        user.delete()

    return redirect(url_for("logout"))
