from application import models

models.engine = models.set_default_uri(
    f"sqlite:///:memory:"
)
