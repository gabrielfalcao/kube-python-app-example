import os
import redis


REDIS_HOST = os.getenv("REDIS_HOST")
if REDIS_HOST:
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.Redis(
        host=REDIS_HOST or "localhost",
        port=int(os.getenv("REDIS_PORT") or 6379),
        db=0,
    )
else:
    SESSION_TYPE = "null"


SECRET_KEY = b"c]WNEy-&?;NN%UzOc"

AUTH0_DOMAIN = "dev-newstore.auth0.com"
AUTH0_CALLBACK_URI = (
    "https://newstoresauth0ldap.ngrok.io/callback/auth0")
AUTH0_CLIENT_ID = "1J2tdk1J6hjloR3arVH4cZHfOor71uab"
AUTH0_CLIENT_SECRET = (
    "O3-tFXQSf0L9Z-dNq4XQ0gFEboJJQQYwnd9eKVKKbX3FhGIAfWgUOkBcStQKSyp2"
)

# https://manage.auth0.com/dashboard/us/dev-newstore/apis/5e2a25ea4d0204077e6a2fd5/settings
AUTH0_API_ID = '5e2a25ea4d0204077e6a2fd5'
AUTH0_API_IDENTIFIER = "https://NA-40801/poc-ldap"
