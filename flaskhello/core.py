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
        return f"postgresql+psycopg2://{config.auth}@{config.domain}/{config.database}"


params = {"template_folder": templates_path}

application = Flask(__name__, **params)

cors = CORS(application, resources="/*")

session = Session(application)
oauth = OAuth(application)

auth0 = oauth.register(
    "auth0",
    client_id="N6l4Wi2JmIh5gXiGj2sibsZiJRJu0jj1",
    client_secret="QaAD-WTxpqa3xUChuqyYiEL1d0bnDuusJvtij_cxgiZ9gBtww5QMkKoeabHpuwsL",
    api_base_url="https://dev-newstore.auth0.com",
    access_token_url="https://dev-newstore.auth0.com/oauth/token",
    authorize_url="https://dev-newstore.auth0.com/authorize",
    client_kwargs={"scope": "openid profile email"},
)

application.config["SESSION_REDIS"] = redis.Redis(
    host=os.getenv("REDIS_HOST") or "localhost",
    port=int(os.getenv("REDIS_PORT") or 6379),
    db=0,
)
application.config["SESSION_TYPE"] = "redis"
application.config["AUTH0_DOMAIN"] = "dev-newstore.auth0.com"
application.config["API_IDENTIFIER"] = "https://dev-ldap-py"

application.config["AUTH0_CALLBACK_URI"] = "https://newstoresauth0ldap.ngrok.io"
application.config["AUTH0_CLIENT_ID"] = "N6l4Wi2JmIh5gXiGj2sibsZiJRJu0jj1"
application.config[
    "AUTH0_CLIENT_SECRET"
] = "QaAD-WTxpqa3xUChuqyYiEL1d0bnDuusJvtij_cxgiZ9gBtww5QMkKoeabHpuwsL"
