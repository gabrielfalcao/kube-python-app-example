import os
import logging

if not os.getenv("GEVENT_DISABLED"):
    import gevent.monkey

    gevent.monkey.patch_all()
else:
    logging.warning(
        "GEVENT_DISABLED env var is set, gevent will not monkey-patch things"
    )
