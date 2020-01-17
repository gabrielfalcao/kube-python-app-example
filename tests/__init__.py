from application import models

models.engine = models.set_default_uri(f"sqlite:///:memory:")

models.metadata.create_all(models.engine)
