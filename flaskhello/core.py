import os
import redis
from flask import Flask
from flask_cors import CORS
from flask_session import Session
from authlib.flask.client import OAuth

from flaskhello.filesystem import templates_path


class config:
    host = os.getenv("POSTGRES_HOST") or "localhost"
    port = int(os.getenv("POSTGRES_PORT") or 5432)
    username = os.getenv("POSTGRES_USERNAME") or "flask_hello"
    password = os.getenv("POSTGRES_PASSWORD") or ""
    database = os.getenv("POSTGRES_DATABASE") or "flask_hello"
    auth = os.getenv("POSTGRES_AUTH") or (
        password and f"{username}:{password}" or username
    )
    domain = os.getenv("POSTGRES_DOMAIN") or f"{host}:{port}"

    @classmethod
    def sqlalchemy_url(config):
        return "/".join([
            f"postgresql+psycopg2:/",
            f"{config.auth}@{config.domain}",
            f"{config.database}"
        ])


params = {
    "template_folder": templates_path,
    "static_url_path": '',
    "static_folder": 'web/static',
}

application = Flask(__name__, **params)
application.config.from_object('flaskhello.config')

cors = CORS(application, resources="/*")

session = Session(application)
oauth = OAuth(application)

auth0 = oauth.register(
    "auth0",
    client_id=application.config["AUTH0_CLIENT_ID"],
    client_secret=application.config["AUTH0_CLIENT_SECRET"],
    api_base_url="https://dev-newstore.auth0.com",
    access_token_url="https://dev-newstore.auth0.com/oauth/token",
    authorize_url="https://dev-newstore.auth0.com/authorize",
    client_kwargs={"scope": "openid profile email"},
)
