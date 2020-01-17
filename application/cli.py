# -*- coding: utf-8 -*-
import os
import sys
import click
import logging
import coloredlogs
from chemist import set_default_uri
from application.core import application, config
from application.models import metadata
from application import version


logger = logging.getLogger(__name__)

level_choices = click.Choice(
    ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
)


@click.group()
@click.option("--loglevel", default="INFO", type=level_choices)
@click.pass_context
def main(ctx, loglevel):
    "flask-hello command-line manager"
    coloredlogs.install(level=loglevel)

    ctx.obj = dict(engine=set_default_uri(config.sqlalchemy_url()))


@main.command(name="version")
def print_version():
    "prints the version to the STDOUT"
    print(f"flask-hello {version} / {sys.platform}")


@main.command("check")
def check():
    "runs the web server"

    coloredlogs.install(level="DEBUG")
    logger.info('IT WORKS!')


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
        coloredlogs.install(level="DEBUG")

    application.run(debug=debug, host=host, port=port)


@main.command("check-db")
@click.pass_context
def check_db(ctx):
    "attempts to connect to database"

    coloredlogs.install(level="DEBUG")
    engine = ctx.obj["engine"]
    url = engine.url
    logger.info(f"Trying to connect to DB")
    try:
        result = engine.connect()
        logger.info(f"SUCCESS: {url}")
    except Exception as e:
        logger.exception(
            f"failed to connect to {url}: {e}"
        )
        raise SystemExit(1)


@main.command("migrate-db")
@click.pass_context
def migrate_db(ctx):
    "runs the web server"

    coloredlogs.install(level="DEBUG")
    engine = ctx.obj["engine"]
    url = engine.url
    logger.info(f"Migrating SQL database")
    try:
        metadata.create_all(engine, checkfirst=False)
        logger.info(f"SUCCESS")
    except Exception as e:
        logger.exception(
            f"failed to connect to migrate {url}: {e}"
        )
        raise SystemExit(1)
