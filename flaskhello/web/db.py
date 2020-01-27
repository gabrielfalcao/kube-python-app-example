import json
from typing import Tuple
from flask import jsonify
from flaskhello.models import User, UserToken
from .core import application


class BackendError(Exception):
    def __init__(self, message, status_code: int):
        super().__init__(message)
        self.status_code = status_code


class ValidationError(BackendError):
    def __init__(self, message, status_code: int = 400):
        super().__init__(message, status_code)


@application.errorhandler(BackendError)
def handle_error(error):
    response = {
        'error': str(error)
    }
    return jsonify(response), error.status_code


def get_user_and_token_from_userinfo(
        userinfo: dict,
        token: dict,
) -> Tuple[User, UserToken]:

    if not isinstance(userinfo, dict):
        raise ValidationError(f"userinfo must be a dict, got: {userinfo!r}")

    email = userinfo.pop('email', None)
    if not isinstance(email, str):
        raise ValidationError(f"userinfo['email'] must be a string, got: {email!r}")

    if not email:
        raise ValidationError(f"email cannot be empty")

    if not isinstance(token, dict):
        raise ValidationError(f"token must be a dict, got: {token!r}")

    user = User.get_or_create(email=email)

    token = user.add_token(**token)

    oauth2_id = userinfo.pop("sub", None)  # might be auth0-specific,
    # check for keycloak
    if oauth2_id:
        user.set(oauth2_id=oauth2_id)

    for field in ("name", "picture"):
        value = userinfo.pop(field, None)
        if value:
            user.set(**{field: value})

    user.update_and_save(
        extra_data=json.dumps(userinfo, indent=4, default=str)
    )
    return user, token


def get_user_and_token_from_access_token(
        access_token: str
) -> Tuple[User, UserToken]:

    if not access_token:
        raise ValidationError(f"invalid access token {access_token!r}")

    token = UserToken.find_one_by(access_token=access_token)
    if not token:
        raise BackendError(f'token not found', 401)

    return token.user, token
