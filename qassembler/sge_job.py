import logging
import os
from typing import Dict, List, Any

from docker import client
from flasgger import SwaggerView
from flask import jsonify, request, make_response
from marshmallow import Schema, fields

from qassembler.config import GOLDEN_BINARY_DIR_NAME, \
    GOLDEN_REFERENCES_DIR_NAME, PROJECT_DIRECTORIES, PROJECT_PREFIX, \
    SHARED_VOLUME_PATH, SSH_VOLUME_PATH
from qassembler.utils import generate_sge_job_params, \
    create_directory_structure, \
    create_param_file, update_job_status
from qassembler.job_status import JobStatus

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
        working_directory = os.path.join(SHARED_VOLUME_PATH,
                                         PROJECT_PREFIX,
                                         sge_job_params.job_name)
        log.info(f'Host\'s working directory is {working_directory}')
        create_directory_structure(working_directory,
                                   PROJECT_DIRECTORIES)
        log.info(f'The follwing directories {PROJECT_DIRECTORIES}'
                 f' created in project {sge_job_params.job_name}')
        update_job_status(working_directory, JobStatus.PROJECT_CREATED)
        log.info(f'Update Job status to {JobStatus.PROJECT_CREATED}')

        create_param_file(working_directory, sge_job_params)

        response = self.docker_client.containers.run(
            image='qommunicator:latest',
            name=sge_job_params.job_name,
            volumes={
                working_directory: {
                    'bind': os.path.join(SHARED_VOLUME_PATH,
                                         PROJECT_PREFIX,
                                         sge_job_params.job_name),
                    'mode': 'rw'},
                SSH_VOLUME_PATH: {
                    'bind': '/ssh-volume',
                    'mode': 'ro'},
                sge_job_params.golden_binary_path: {
                    'bind': os.path.join(SHARED_VOLUME_PATH,
                                         GOLDEN_BINARY_DIR_NAME),
                    'mode': 'ro'},
                sge_job_params.golden_reference_path: {
                    'bind': os.path.join(SHARED_VOLUME_PATH,
                                         GOLDEN_REFERENCES_DIR_NAME),
                    'mode': 'ro'},
            },
            links={'gridengine': None},
            environment={
                "GRIDENGINE_USER": 'root',
                "GRIDENGINE_SSH_KEY_PATH": os.path.join('/ssh-volume',
                                                        'sge_rsa'),
                "PARAM_FILE_PATH": os.path.join(SHARED_VOLUME_PATH,
                                                PROJECT_PREFIX,
                                                sge_job_params.job_name,
                                                'param_file.json')
            },
            detach=True
        )
        log.info(response)
        update_job_status(working_directory, JobStatus.DOCKER_STARTED)
        log.info(f'Job status updated to {JobStatus.DOCKER_STARTED}')

        return make_response(
            jsonify(
                {
                    'job_name': sge_job_params.job_name
                }
            ),
            201)
