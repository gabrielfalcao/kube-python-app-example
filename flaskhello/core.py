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
application.config["SESSION_REDIS"] = redis.Redis(
    host=os.getenv("REDIS_HOST") or "localhost",
    port=int(os.getenv("REDIS_PORT") or 6379),
    db=0,
)
application.config["SECRET_KEY"] = b"c]WNEy-&?;NN%UzOc"
application.config["SESSION_TYPE"] = "redis"
application.config["AUTH0_DOMAIN"] = "dev-newstore.auth0.com"
application.config["AUTH0_CALLBACK_URI"] = (
    "https://newstoresauth0ldap.ngrok.io/callback/auth0")
application.config["AUTH0_CLIENT_ID"] = "N6l4Wi2JmIh5gXiGj2sibsZiJRJu0jj1"
application.config["AUTH0_CLIENT_SECRET"] = (
    "QaAD-WTxpqa3xUChuqyYiEL1d0bnDuusJvtij_cxgiZ9gBtww5QMkKoeabHpuwsL"
)

# https://manage.auth0.com/dashboard/us/dev-newstore/apis/5e2a25ea4d0204077e6a2fd5/settings
application.config["AUTH0_API_ID"] = '5e2a25ea4d0204077e6a2fd5'
application.config["AUTH0_API_IDENTIFIER"] = "https://NA-40801/poc-ldap"

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
