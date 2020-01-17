import logging
from application.models import metadata, engine


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    print("Migrating database")
    metadata.create_all(engine)
    print("DONE")


if __name__ == '__main__':
    main()
