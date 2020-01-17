import os
from datetime import datetime
from chemist import (
    Model, db, metadata,
    set_default_uri,
)


class config:
    host = os.getenv('POSTGRES_HOST') or 'localhost'
    port = os.getenv('POSTGRES_PORT') or 5432
    username = os.getenv('POSTGRES_USERNAME') or 'flask_hello'
    password = os.getenv('POSTGRES_PASSWORD') or ''
    database = os.getenv('POSTGRES_DATABASE') or 'flask_hello'
    auth = os.getenv('POSTGRES_AUTH') or (password and f'{username}:{password}' or username)
    domain = os.getenv('POSTGRES_DOMAIN') or f'{host}:{port}'


engine = set_default_uri(
    f"postgresql+psycopg2://{config.auth}@{config.domain}/{config.database}"
)


class User(Model):
    table = db.Table('user', metadata,
        db.Column('id', db.Integer, primary_key=True),
        db.Column('email', db.String(100), nullable=False, unique=True),
        db.Column('password', db.String(100), nullable=False),
        db.Column('created_at', db.DateTime, default=datetime.utcnow),
        db.Column('updated_at', db.DateTime, default=datetime.utcnow)
    )
