from flask import Flask
from flask_cors import CORS
from flask_session import Session
from authlib.integrations.flask_client import OAuth

from flaskhello.filesystem import templates_path


params = {
    "template_folder": templates_path,
    "static_url_path": "",
    "static_folder": "web/static",
}

application = Flask(__name__, **params)
application.config.from_object("flaskhello.config")

cors = CORS(application, resources="/*")

session_manager = Session(application)
oauth = OAuth(application)

auth0 = oauth.register(
    "identity_provider",
    client_id=application.config["OAUTH2_CLIENT_ID"],
    client_secret=application.config["OAUTH2_CLIENT_SECRET"],
    api_base_url=application.config["OAUTH2_BASE_URL"],
    access_token_url=application.config["OAUTH2_ACCESS_TOKEN_URL"],
    authorize_url=application.config["OAUTH2_AUTHORIZE_URL"],
    client_kwargs={
        "scope": application.config["OAUTH2_CLIENT_SCOPE"],
        "audience": application.config["OAUTH2_CLIENT_AUDIENCE"]
    },
)
