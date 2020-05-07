import json
import logging

from datetime import datetime
from chemist import context
from chemist import Model, db, metadata, DefaultForeignKey


logger = logging.getLogger(__name__)


class TestTest(Model):
    table = db.Table(
        "testtest",
        metadata,
        db.Column("id", db.Integer, primary_key=True),
        db.Column("field1", db.DateTime, default=datetime.utcnow),
        db.Column("field2", db.DateTime, default=datetime.utcnow),
    )


def test_insert_data():
    context.set_default_uri(
        'postgresql+psycopg2://doctor_who:timemachine@localhost:5432/doctor_who')

    row = TestTest.create()

    import ipdb;ipdb.set_trace()
