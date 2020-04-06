import logging
import os
from typing import Dict, List

from docker import client
from flasgger import SwaggerView
from flask import jsonify, request, make_response
from marshmallow import Schema, fields

from qassembler.utils import render_qsub_template, \
    generate_sge_job_params, create_directory_structure, \
    create_qsub_job_file

log = logging.getLogger(__name__)


class SgeJobSchema(Schema):
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
        pipeline: List[Dict[str, str]] = SgeJobSchema().load(request.json)
        log.info(f'sge job pipeline request: {pipeline}')

        sge_job_params = generate_sge_job_params(pipeline)
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

        # shared_volume = {
        #     HOST_SHARED_VOLUME_PATH: {
        #         'bind': CONTAINER_SHARED_VOLUME_PATH,
        #         'mode': 'rw',
        #     },
        # }

        # response = self.docker_client.containers.run(
        #     image='alpine',
        #     name=job_name,
        #     volumes=shared_volume,
        #     command='sleep 3'
        # )
        # print(response)

        return make_response(
            jsonify(
                {
                    'job_name': sge_job_params.job_name
                }
            ),
            201)
