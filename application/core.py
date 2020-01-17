import os
import redis
from flask import Flask
from flask_cors import CORS
from flask_session import Session

from application.filesystem import templates_path


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


application.config['SESSION_REDIS'] = redis.Redis(
    host=os.getenv('REDIS_HOST') or 'localhost',
    port=int(os.getenv('REDIS_PORT') or 6379),
    db=0,
)
application.config['SESSION_TYPE'] = 'redis'
