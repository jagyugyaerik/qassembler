import logging
import os
from typing import Dict, List, Any

from docker import client
from flasgger import SwaggerView
from flask import jsonify, request, make_response
from marshmallow import Schema, fields

from qassembler.config import CONTAINER_SHARED_VOLUME_PATH, \
    HOST_SSH_VOLUME_PATH, \
    CONTAINER_SSH_VOLUME_PATH
from qassembler.utils import render_qsub_template, \
    generate_sge_job_params, create_directory_structure, \
    create_qsub_job_file, create_param_file

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

        list_of_directories = [sge_job_params.working_directory_path,
                               sge_job_params.output_path,
                               sge_job_params.error_path,
                               sge_job_params.binaries_path,
                               sge_job_params.reference_path]
        create_directory_structure(sge_job_params.working_directory_path,
                                   list_of_directories)
        log.info(f'The following directories created {list_of_directories}')

        qsub_job = render_qsub_template(sge_job_params)
        qsub_filename = os.path.join(sge_job_params.working_directory_path,
                                     'qsub_job.submit')
        create_qsub_job_file(qsub_filename, qsub_job)
        log.info(f'qsub job: {qsub_job}')

        create_param_file(sge_job_params)

        response = self.docker_client.containers.run(
            image='qommunicator:latest',
            name=sge_job_params.job_name,
            volumes={
                sge_job_params.working_directory_path: {
                    'bind': os.path.join(CONTAINER_SHARED_VOLUME_PATH,
                                         sge_job_params.job_name),
                    'mode': 'rw'},
                HOST_SSH_VOLUME_PATH: {
                    'bind': CONTAINER_SSH_VOLUME_PATH,
                    'mode': 'ro'}
            },
            links={'gridengine':None},
            environment={
                "GRIDENGINE_USER": 'root',
                "GRIDENGINE_SSH_KEY_PATH": os.path.join(
                    CONTAINER_SHARED_VOLUME_PATH, '.ssh', 'sge_rsa'),
                "PARAM_FILE_PATH": sge_job_params.param_file_path
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
