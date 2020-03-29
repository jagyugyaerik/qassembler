import logging

from flasgger import LazyJSONEncoder
from flask import Flask

log = logging.getLogger(__name__)


def main() -> Flask:
    logging.basicConfig(
        format='[%(asctime)s] [%(process)d] [%(levelname)s] '
               '%(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S %z',
        level=logging.DEBUG)

    log.info("Starting qassembler")

    app = Flask("__name__")
    app.json_encoder = LazyJSONEncoder

    return app


app = main()
