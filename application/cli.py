# -*- coding: utf-8 -*-
import os
import sys
import json
import socket
import click
import logging
import coloredlogs
from chemist import set_default_uri
from application.core import application, config
from application.models import metadata
from application import version


level_choices = click.Choice(
    ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
)


def check_database_dns():
    try:
        logger.info(f"Check ability to resolve name: {config.host}")
        host = socket.gethostbyname(config.host)
        logger.info(f"SUCCESS: {config.host!r} => {host!r}")
    except Exception as e:
        return e

    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # try:
    #     logger.info(f"Checking TCP connection to {host!r}")
    #     sock.connect((host, int(config.port)))
    #     logger.info(f"SUCCESS: TCP connection to database works!!")
    # except Exception as e:
    #     return e
    # finally:
    #     sock.close()


def set_log_level_by_name(loglevel: str, loggername=None):
    loglevel = loglevel.upper()
    coloredlogs.install(loglevel)
    if loggername:
        logger = logging.getLogger(loggername)
    else:
        logger = logging.getLogger()

    logger.setLevel(getattr(logging, loglevel.upper(), logging.INFO))


def set_debug_mode():
    # logging.getLogger().addHandler(logging.StreamHandler(sys.stderr))
    set_log_level_by_name("DEBUG")


logger = logging.getLogger("flask-hello")


@click.group()
@click.option("--loglevel", default="INFO", type=level_choices)
@click.pass_context
def main(ctx, loglevel):
    "flask-hello command-line manager"
    set_log_level_by_name(loglevel)
    ctx.obj = dict(engine=set_default_uri(config.sqlalchemy_url()))


@main.command(name="version")
def print_version():
    "prints the version to the STDOUT"
    print(f"flask-hello {version} / {sys.platform}")


@main.command("check")
def check():
    "runs the web server"

    set_debug_mode()
    logger.info("Python installation works!")
    logger.info(f"DATABASE HOSTNAME: {config.sqlalchemy_url()!r}")
    env = json.dumps(dict(os.environ), indent=4)
    print(f'\033[1;33m{env}\033[0m')


@main.command("web")
@click.option(
    "--port",
    "-p",
    help="HTTP PORT",
    type=int,
    default=int(os.getenv("FLASK_PORT", 5000)),
)
@click.option(
    "--host", "-H", help="HTTP HOST", default=str(os.getenv("FLASK_HOST", "0.0.0.0"))
)
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    help="enable debug mode (should not use in production)",
    default=bool(os.getenv("FLASK_DEBUG")),
)
@click.pass_context
def run_web(ctx, host, port, debug):
    "runs the web server"

    if debug:
        set_debug_mode()

    application.run(debug=debug, host=host, port=port)


@main.command("check-db")
@click.pass_context
def check_db(ctx):
    "checks if the application can connect to the configured db"

    set_debug_mode()

    error = check_database_dns()
    if error:
        logger.error(f'could not resolve {config.host!r}: {error}')
        raise SystemExit(1)

    engine = ctx.obj["engine"]
    url = engine.url
    logger.info(f"Trying to connect to DB")
    result = engine.connect()
    logger.info(f"SUCCESS: {url}")
    result.close()


@main.command("migrate-db")
@click.pass_context
def migrate_db(ctx):
    "runs the web server"

    set_debug_mode()
    error = check_database_dns()
    if error:
        logger.error(f'could not resolve {config.host!r}: {error}')
        raise SystemExit(1)

    engine = ctx.obj["engine"]
    url = engine.url
    logger.info(f"Migrating SQL database: {str(engine.url)!r}")
    try:
        metadata.create_all(engine)
        logger.info(f"SUCCESS")
    except Exception as e:
        logger.exception(f"failed to connect to migrate {url}: {e}")
