from flask import Flask

from application.filesystem import templates_path


params = {"template_folder": templates_path}

application = Flask(__name__, **params)
