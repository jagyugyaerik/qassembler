import logging
import json
from http import HTTPStatus

from docker import client
from flask import Flask, make_response, redirect
from werkzeug.wrappers import Response
from marshmallow.exceptions import ValidationError
from flasgger import Swagger, LazyJSONEncoder

from qassembler.config import QASSEMBLER_VERSION, DATE_FMT
from qassembler.sge_job import SgeJobView
from qassembler.job_status import JobStatusView

log = logging.getLogger(__name__)


def healthz() -> Response:
    return Response("Ok\n", status=200)


def _handle_exception(exc: Exception):  # type: ignore
    body = json.dumps({
        "error": str(exc)
    })
    headers = {
        "Content-Type": "application/json"
    }
    log.warning(f'Exception while handling user request', exc_info=exc)
    status = HTTPStatus.BAD_REQUEST.value
    return make_response(body, status, headers)


def handle_validation_error(exc: ValidationError):  # type: ignore
    return _handle_exception(exc)


def handle_value_error(exc: ValueError):  # type: ignore
    return _handle_exception(exc)


def index() -> Response:
    return redirect('apidocs')


def init_docker_client() -> client:
    return client.from_env()


def create_app_routes(app: Flask, docker_client: client) -> None:
    log.info("Creating API Routes")
    app.add_url_rule('/healthz', 'healthz', healthz)
    app.add_url_rule('/', 'index', index)
    app.add_url_rule('/sge_job',
                     view_func=SgeJobView.as_view('sge_job', docker_client),
                     methods=['POST'])
    app.add_url_rule('/job_status/<job_name>',
                     view_func=JobStatusView.as_view('job_status'),
                     methods=['GET'])
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(ValueError, handle_value_error)


def main() -> Flask:
    logging.basicConfig(
        format='[%(asctime)s] [%(process)d] [%(levelname)s] '
               '%(name)s: %(message)s',
        datefmt=DATE_FMT,
        level=logging.DEBUG)

    log.info(f"Starting qassembler {QASSEMBLER_VERSION}")

    docker_client = init_docker_client()
    app = Flask("__name__")
    app.json_encoder = LazyJSONEncoder
    app.config['SWAGGER'] = {
        'title': 'QAssembler',
        'description': 'QAssembler',
        'version': QASSEMBLER_VERSION,
        'uiversion': 3
    }
    Swagger(app)

    create_app_routes(app, docker_client)

    return app


app = main()
