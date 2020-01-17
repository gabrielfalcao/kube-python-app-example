import logging
from application.models import metadata, engine


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    metadata.create_all(engine)


if __name__ == '__main__':
    main()
