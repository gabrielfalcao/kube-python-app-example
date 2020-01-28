import os
import redis


APP_URL_EXTERNAL = os.getenv("APP_URL_EXTERNAL") or "https://newstore-auth0-test.ngrok.io/"

REDIS_HOST = os.getenv("REDIS_HOST")
if REDIS_HOST:
    SESSION_TYPE = "filesystem"
    SESSION_REDIS = redis.Redis(
        host=REDIS_HOST or "localhost", port=int(os.getenv("REDIS_PORT") or 6379), db=0
    )
else:
    SESSION_TYPE = "filesystem"

# set this to true when serving the application via HTTPS or else the
# flask-restful routes won't show up on swagger.
HTTPS_API = os.getenv("HTTPS_API")

SECRET_KEY = b"c]WNEy-&?;NN%UzOc"

OAUTH2_DOMAIN = os.getenv("OAUTH2_DOMAIN") or "dev-newstore.auth0.com"
OAUTH2_CALLBACK_URL = (
    os.getenv("OAUTH2_CALLBACK_URL")
    or "https://newstore-auth0-test.ngrok.io/callback/auth0"
)

# https://manage.auth0.com/dashboard/us/dev-newstore/applications/N6l4Wi2JmIh5gXiGj2sibsZiJRJu0jj1/settings
OAUTH2_CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID")
OAUTH2_CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET")
OAUTH2_BASE_URL = os.getenv("OAUTH2_BASE_URL") or "https://dev-newstore.auth0.com"
OAUTH2_ACCESS_TOKEN_URL = (
    os.getenv("OAUTH2_ACCESS_TOKEN_URL") or f"{OAUTH2_BASE_URL}/oauth/token"
)
OAUTH2_AUTHORIZE_URL = (
    os.getenv("OAUTH2_AUTHORIZE_URL") or "{OAUTH2_BASE_URL}/authorize"
)
OAUTH2_CLIENT_SCOPE = os.getenv("OAUTH2_CLIENT_SCOPE") or "openid profile email read:user write:user browse:api"
OAUTH2_CLIENT_AUDIENCE = os.getenv("OAUTH2_CLIENT_AUDIENCE") # or "https://newstore-auth0-test.ngrok.io/"


class dbconfig:
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
        return "/".join(
            [
                f"postgresql+psycopg2:/",
                f"{config.auth}@{config.domain}",
                f"{config.database}",
            ]
        )
