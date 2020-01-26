import json
import logging
from datetime import datetime
from chemist import Model, db, metadata, DefaultForeignKey


logger = logging.getLogger(__name__)


def ensure_datetime(value):
    if isinstance(value, str):
        try:
            value = int(value)
        except (TypeError, ValueError):
            logger.warning(
                f'cannot convert timestamp to datetime: {value!r}. '
                'Datetime will be NULL.'
            )
            return None

    if isinstance(value, (float, int)):
        return datetime.fromtimestamp(value)

    elif isinstance(value, datetime):
        return value

    return value


class User(Model):
    table = db.Table(
        "user",
        metadata,
        db.Column("id", db.Integer, primary_key=True),
        db.Column("email", db.String(100), nullable=False, unique=True),

        db.Column("name", db.String(255)),
        db.Column("picture", db.UnicodeText),
        db.Column("created_at", db.DateTime, default=datetime.utcnow),
        db.Column("updated_at", db.DateTime, default=datetime.utcnow),
        db.Column("extra_data", db.UnicodeText),
    )

    def to_dict(self):
        data = self.serialize()
        data['extra_data'] = self.extra_data
        return data

    @property
    def extra_data(self):
        value = self.get('extra_data')
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            logger.warning(f'{self}.extra_data is not a valid JSON')
            return {
                'value': value,
                'error': str(e)
            }

    def save(self, *args, **kw):
        self.set(updated_at=datetime.utcnow())
        return super().save(*args, **kw)

    def add_token(self, id_token: str, access_token: str, expires_in: int, expires_at: datetime, scope: str, token_type: str, **extra_data):
        token = UserToken.get_or_create(
            user_id=self.id,
            id_token=id_token,
        )
        return token.update_and_save(
            access_token=access_token,
            expires_at=ensure_datetime(expires_at),
            expires_in=expires_in,
            scope=scope,
            token_type=token_type,
            extra_data=json.dumps(extra_data, indent=4, default=str)
        )


class UserToken(Model):
    table = db.Table(
        'user_tokens', metadata,

        db.Column("id", db.Integer, primary_key=True),
        db.Column("oauth2_id", db.UnicodeText, nullable=True, index=True),
        db.Column("id_token", db.UnicodeText, nullable=True),
        db.Column("access_token", db.UnicodeText, nullable=True, index=True),
        db.Column("expires_at", db.DateTime),
        db.Column("expires_in", db.Integer),
        db.Column("scope", db.Text),
        db.Column("token_type", db.Text),
        db.Column("extra_data", db.UnicodeText),
        DefaultForeignKey('user_id', 'user.id'),
    )

    @property
    def user(self):
        return User.find_one_by(id=self.user_id)

    @property
    def extra_data(self):
        value = self.get('extra_data')
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            logger.warning(f'{self}.extra_data is not a valid JSON')
            return {
                'value': value,
                'error': str(e)
            }

    def to_dict(self):
        data = self.serialize()
        data['extra_data'] = self.extra_data
        return data
