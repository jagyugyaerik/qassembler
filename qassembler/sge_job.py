import logging
from datetime import datetime
from typing import NamedTuple

from docker import client
from flasgger import SwaggerView
from flask import jsonify, request, make_response
from marshmallow import Schema, fields

from qassembler.config import HOST_SHARED_VOLUME_PATH, \
    CONTAINER_SHARED_VOLUME_PATH

log = logging.getLogger(__name__)

SgeJobParams = NamedTuple('SgeJobParams',
                          [('shell_binary_path', str),
                           ('output_path', str),
                           ('error_path', str),
                           ('working_dir_path', str)])


class SgeJobSchema(Schema):
    shell_binary_path = fields.Str(required=True, default="/bin/bash")
    output_path = fields.Str()
    error_path = fields.Str()
    working_dir_path = fields.Str()


class SgeJobResponse(Schema):
    job_name = fields.Str()


class SgeJobView(SwaggerView):  # type: ignore
    tags = ['sge_job']
    parameters = SgeJobSchema
    responses = {
        201: {
            'description': "Created unit test job's name(s)",
            'schema': SgeJobResponse
        }
    }

    def __init__(self, docker_client: client) -> None:
        self.docker_client = docker_client

    def post(self):  # type: ignore
        """
        Start a sge job
        """
        params: SgeJobParams = SgeJobSchema().load(request.json)
        log.info(f'sge job request: {params}')

        job_name = 'sge-{:%Y%m%d-%H%M%S-%f}'.format(datetime.now())

        shared_volume = {
            HOST_SHARED_VOLUME_PATH: {
                'bind': CONTAINER_SHARED_VOLUME_PATH,
                'mode': 'rw',
            },
        }

        response = self.docker_client.containers.run(
            image='alpine',
            name=job_name,
            volumes=shared_volume,
            command='sleep 3000'
        )
        print(response)

        return make_response(
            jsonify(
                {
                    'job_name': job_name
                }
            ),
            201)
