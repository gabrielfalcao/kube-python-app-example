# -*- coding: utf-8 -*-
import os
import time
import sys
import json
import socket
import click
import logging
import coloredlogs
import gevent.monkey
import zmq
from zmq.devices import Device
from chemist import set_default_uri
from application.web import application
from application.core import config
from application.models import metadata
from application.worker.client import EchoClient
from application.worker.server import EchoServer
from application import version


DEFAULT_ROUTER_PORT = os.getenv("ZMQ_ROUTER_PORT") or 4242
DEFAULT_ROUTER_HOST = os.getenv("ZMQ_ROUTER_HOST") or "0.0.0.0"

DEFAULT_ROUTER_ADDRESS = os.getenv("ZMQ_ROUTER_ADDRESS") or (
    f"tcp://{DEFAULT_ROUTER_HOST}:{DEFAULT_ROUTER_PORT}"
)

DEFAULT_DEALER_PORT = os.getenv("ZMQ_DEALER_PORT") or 6969
DEFAULT_DEALER_HOST = os.getenv("ZMQ_DEALER_HOST") or "0.0.0.0"

DEFAULT_DEALER_ADDRESS = os.getenv("ZMQ_DEALER_ADDRESS") or (
    f"tcp://{DEFAULT_DEALER_HOST}:{DEFAULT_DEALER_PORT}"
)


level_choices = click.Choice(
    ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
)


def check_db_connection(engine):
    url = engine.url
    logger.info(f"Trying to connect to DB: {str(url)!r}")
    result = engine.connect()
    logger.info(f"SUCCESS: {url}")
    result.close()


def check_database_dns():
    try:
        logger.info(f"Check ability to resolve name: {config.host}")
        host = socket.gethostbyname(config.host)
        logger.info(f"SUCCESS: {config.host!r} => {host!r}")
    except Exception as e:
        return e

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        logger.info(f"Checking TCP connection to {host!r}")
        sock.connect((host, int(config.port)))
        logger.info(f"SUCCESS: TCP connection to database works!!")
    except Exception as e:
        return e
    finally:
        sock.close()


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
    gevent.monkey.patch_all()
    set_log_level_by_name(loglevel)
    ctx.obj = dict(engine=set_default_uri(config.sqlalchemy_url()))


@main.command(name="version")
def print_version():
    "prints the version to the STDOUT"
    print(f"flask-hello {version} / {sys.platform}")


@main.command("check")
def check():
    "checks python installation"

    set_debug_mode()
    logger.info("Python installation works!")
    logger.info(f"DATABASE HOSTNAME: {config.sqlalchemy_url()!r}")
    env = json.dumps(dict(os.environ), indent=4)
    print(f"\033[1;33m{env}\033[0m")


@main.command("web")
@click.option(
    "--port",
    "-p",
    help="HTTP PORT",
    type=int,
    default=int(os.getenv("FLASK_PORT", 5000)),
)
@click.option("--host", "-H", help="HTTP HOST", default=os.getenv("FLASK_HOST"))
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

    application.run(debug=debug, host=host or None, port=port)


@main.command("check-db")
@click.pass_context
def check_db(ctx):
    "checks if the application can connect to the configured db"

    set_debug_mode()

    error = check_database_dns()
    if error:
        logger.error(f"could not resolve {config.host!r}: {error}")
        raise SystemExit(1)

    engine = ctx.obj["engine"]
    check_db_connection(engine)


@main.command("migrate-db")
@click.pass_context
def migrate_db(ctx):
    "runs the web server"

    set_debug_mode()
    error = check_database_dns()
    if error:
        logger.error(f"could not resolve {config.host!r}: {error}")
        raise SystemExit(1)

    try:
        check_db_connection(engine)
    except Exception:
        time.sleep(5)

    engine = ctx.obj["engine"]
    url = engine.url
    logger.info(f"Migrating SQL database: {str(engine.url)!r}")
    try:
        metadata.create_all(engine)
        logger.info(f"SUCCESS")
    except Exception as e:
        logger.exception(f"failed to connect to migrate {url}: {e}")


@main.command("worker")
@click.option(
    "--address",
    "-c",
    help="the zeromq address of the router",
    default=DEFAULT_DEALER_ADDRESS,
)
@click.pass_context
def worker(ctx, address):
    "runs a worker"

    server = EchoServer(zmq_uri=address)
    server.run()


@main.command("enqueue", context_settings=dict(ignore_unknown_options=True))
@click.argument("data")
@click.option(
    "--address",
    "-p",
    help="the zeromq address of the router",
    default=DEFAULT_ROUTER_ADDRESS,
)
@click.option("--number", "-n", help="of attempts", type=int, default=5)
@click.option("--times", "-x", help="of execution", type=int, default=1)
@click.pass_context
def enqueue(ctx, address, data, number, times):
    "runs a worker"

    client = EchoClient(zmq_uri=address)

    for x in range(1, times + 1):
        logger.warning(f"request {x}/{times}")
        for i in range(1, number + 1):
            response = client.request(data)
            if response:
                break

            logger.warning(f"attempt {i}/{number}")


@main.command("device")
@click.option(
    "--router",
    help="the zeromq address of the router",
    default=f"tcp://0.0.0.0:{DEFAULT_ROUTER_PORT}",
)
@click.option(
    "--dealer",
    help="the zeromq address of the dealer",
    default=f"tcp://0.0.0.0:{DEFAULT_DEALER_PORT}",
)
@click.pass_context
def device(ctx, router, dealer):
    "runs a worker"

    device = Device(zmq.QUEUE, zmq.ROUTER, zmq.DEALER)
    device.setsockopt_in(zmq.IDENTITY, b"requester")
    device.setsockopt_out(zmq.IDENTITY, b"responder")
    device.bind_in(router)
    device.bind_out(dealer)
    logger.info(f"ROUTER: {router!r}")
    logger.info(f"DEALER: {dealer!r}")
    device.start()
    device.join()
