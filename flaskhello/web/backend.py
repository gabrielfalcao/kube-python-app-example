import requests
from flaskhello import config
from .db import get_user_and_token_from_access_token


class AuthAPIClient(object):
    """currently supports only auth0 but could be extended to support keycloak"""

    def __init__(self, access_token: str, base_url: str):
        self.base_url = base_url
        self.http = requests.Session()
        self.http.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }

    def make_url(self, path):
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def get_roles(self, oauth2_id: str):
        url = self.make_url(f'/api/v2/users/{oauth2_id}/roles')
        response = self.http.get(url)
        return response.json()


def get_roles_from_access_token(access_token):
    user, token = get_user_and_token_from_access_token(access_token)

    return get_roles_from_access_token_and_oauth2_id(
        access_token=access_token,
        oauth2_id=user.oauth2_id,
    )


def get_roles_from_access_token_and_oauth2_id(access_token: str, oauth2_id: str):
    user, token = get_user_and_token_from_access_token(access_token)

    client = AuthAPIClient(
        access_token=access_token,
        base_url=config.OAUTH2_BASE_URL,
    )

    return client.get_roles(oauth2_id)
