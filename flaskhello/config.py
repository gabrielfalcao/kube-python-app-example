import os
import redis


APP_URL_EXTERNAL = 'https://newstoresauth0ldap.ngrok.io/'

REDIS_HOST = os.getenv("REDIS_HOST")
if REDIS_HOST:
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.Redis(
        host=REDIS_HOST or "localhost", port=int(os.getenv("REDIS_PORT") or 6379), db=0
    )
else:
    SESSION_TYPE = "filesystem"


SECRET_KEY = b"c]WNEy-&?;NN%UzOc"

OAUTH2_DOMAIN = "dev-newstore.auth0.com"
OAUTH2_CALLBACK_URL = "https://newstoresauth0ldap.ngrok.io/callback/auth0"

# https://manage.auth0.com/dashboard/us/dev-newstore/applications/N6l4Wi2JmIh5gXiGj2sibsZiJRJu0jj1/settings
OAUTH2_CLIENT_ID = "N6l4Wi2JmIh5gXiGj2sibsZiJRJu0jj1"
OAUTH2_CLIENT_SECRET = "QaAD-WTxpqa3xUChuqyYiEL1d0bnDuusJvtij_cxgiZ9gBtww5QMkKoeabHpuwsL"
OAUTH2_BASE_URL = "https://dev-newstore.auth0.com"
OAUTH2_ACCESS_TOKEN_URL = "https://dev-newstore.auth0.com/oauth/token"
OAUTH2_AUTHORIZE_URL = "https://dev-newstore.auth0.com/authorize"
OAUTH2_CLIENT_SCOPE = "openid profile email"


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
