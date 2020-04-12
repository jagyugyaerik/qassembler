import logging
import os
from typing import Dict, List, Any

from docker import client
from flasgger import SwaggerView
from flask import jsonify, request, make_response
from marshmallow import Schema, fields

from qassembler.config import CONTAINER_SHARED_VOLUME_PATH, \
    HOST_SSH_VOLUME_PATH, \
    CONTAINER_SSH_VOLUME_PATH, GOLDEN_BINARY_DIR_NAME, \
    GOLDEN_REFERENCES_DIR_NAME, PROJECT_DIRECTORIES, HOST_SHARED_VOLUME_PATH, \
    PROJECT_PREFIX
from qassembler.utils import generate_sge_job_params, \
    create_directory_structure, \
    create_param_file

log = logging.getLogger(__name__)


class SgeJobSchema(Schema):
    input_files = fields.Str(required=True, default='/home')
    pipeline = fields.List(fields.Dict(keys=fields.Str(), values=fields.Str()))


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
        loaded_schema: Dict[str, Any] = SgeJobSchema().load(request.json)
        pipeline: List[Dict[str, str]] = loaded_schema['pipeline']
        input_path: str = loaded_schema['input_files']

        sge_job_params = generate_sge_job_params(pipeline, input_path)
        log.info(f'sge job params: {sge_job_params}')
        host_working_directory = os.path.join(HOST_SHARED_VOLUME_PATH,
                                              PROJECT_PREFIX,
                                              sge_job_params.job_name)
        log.info(f'Host\'s working directory is {host_working_directory}')
        create_directory_structure(host_working_directory,
                                   PROJECT_DIRECTORIES)
        log.info(f'The follwing directories {PROJECT_DIRECTORIES}'
                 f' created in project {sge_job_params.job_name}')

        create_param_file(host_working_directory, sge_job_params)

        response = self.docker_client.containers.run(
            image='qommunicator:latest',
            name=sge_job_params.job_name,
            volumes={
                host_working_directory: {
                    'bind': os.path.join(CONTAINER_SHARED_VOLUME_PATH,
                                         sge_job_params.job_name),
                    'mode': 'rw'},
                HOST_SSH_VOLUME_PATH: {
                    'bind': CONTAINER_SSH_VOLUME_PATH,
                    'mode': 'ro'},
                sge_job_params.golden_binary_path: {
                    'bind': os.path.join(CONTAINER_SHARED_VOLUME_PATH,
                                         GOLDEN_BINARY_DIR_NAME),
                    'mode': 'ro'},
                sge_job_params.golden_reference_path: {
                    'bind': os.path.join(CONTAINER_SHARED_VOLUME_PATH,
                                         GOLDEN_REFERENCES_DIR_NAME),
                    'mode': 'ro'},
            },
            links={'gridengine':None},
            environment={
                "GRIDENGINE_USER": 'root',
                "GRIDENGINE_SSH_KEY_PATH": os.path.join(
                    CONTAINER_SHARED_VOLUME_PATH, '.ssh', 'sge_rsa'),
                "PARAM_FILE_PATH": os.path.join(CONTAINER_SHARED_VOLUME_PATH,
                                                sge_job_params.job_name,
                                                'param_file.json')
            },
            detach=True
        )
        log.info(response)

        return make_response(
            jsonify(
                {
                    'job_name': sge_job_params.job_name
                }
            ),
            201)
