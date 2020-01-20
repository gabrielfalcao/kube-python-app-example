import os
from datetime import datetime
from elasticsearch import Elasticsearch


ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST") or "localhost"
ELASTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT") or 9200)

es = Elasticsearch([f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}"])
