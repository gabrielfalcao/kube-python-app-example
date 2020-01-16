from chemist import set_default_uri
from application.models import metadata

engine = set_default_uri(f"sqlite:///:memory:")

metadata.create_all(engine)
