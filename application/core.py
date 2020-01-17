from flask import Flask
from flask_cors import CORS

from application.filesystem import templates_path
from application.models import metadata, engine

params = {"template_folder": templates_path}

application = Flask(__name__, **params)
cors = CORS(application, resources="/*")
