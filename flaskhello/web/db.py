import json
from typing import Tuple
from flaskhello.models import User, UserToken


def get_user_and_token_from_userinfo(
        email: str,
        token: dict,
        **extra_data

) -> Tuple[User, UserToken]:

    if not isinstance(email, str):
        raise RuntimeError(f'email must be a string, got: {email!r}')

    if not email:
        raise RuntimeError(f'email cannot be empty')

    if not isinstance(token, dict):
        raise RuntimeError(f'token must be a dict, got: {token!r}')

    user = User.get_or_create(email=email)

    token = user.add_token(**token)

    oauth2_id = extra_data.get('sub')  # might be auth0-specific,
                                       # check for keycloak
    if oauth2_id:
        user.set(oauth2_id=oauth2_id)

    for field in ('name', 'picture'):
        value = extra_data.get(field)
        if value:
            user.set(**{field: value})

    user = user.update_and_save(
        extra_data=json.dumps(
            extra_data,
            indent=4,
            default=str
        )
    )
    return user, token
