import os
from flask import Flask
from flask_cors import CORS

from application.filesystem import templates_path


class config:
    host = os.getenv("POSTGRES_HOST") or "localhost"
    port = os.getenv("POSTGRES_PORT") or 5432
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
