import logging
import os
from enum import Enum
from typing import Tuple, Union, Dict

from flasgger import SwaggerView
from flask import jsonify
from marshmallow import fields, Schema

from qassembler.config import SHARED_VOLUME_PATH, PROJECT_PREFIX

log = logging.getLogger(__name__)


class JobStatus(Enum):
    NOT_FOUND = 'job has not been found'
    PROJECT_CREATED = 'project has been created'
    PENDING = 'pending'
    RUNNING = 'running'
    FINISH = 'finish'


class JobStatusResponse(Schema):
    job_state = fields.Str()


class JobStatusView(SwaggerView):  # type: ignore
    tags = ['sge_job']
    parameters = [
        {
            'name': 'job_name',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'The unique name of the job to query status for',
            'example': 'sge-20200416-154728-561318'
        }
    ]
    responses = {
        200: {
            'description': 'Status of the job',
            'schema': JobStatusResponse
        }
    }

    # pylint: disable=R0201
    def get(self, job_name: str) -> Tuple[Union[str, Dict[str, str]], int]:
        job_status = get_job_status(job_name)
        return jsonify({'job_state': job_status.value}), 200


def get_job_status(job_name: str) -> JobStatus:
    working_directory = os.path.join(SHARED_VOLUME_PATH, PROJECT_PREFIX)
    project_path = os.path.join(working_directory, job_name)
    if not os.path.exists(project_path):
        return JobStatus.NOT_FOUND
    else:
        with open(os.path.join(project_path, 'status'), 'r') as \
                status_file:
            status = status_file.readline()
            try:
                return JobStatus(status)
            except ValueError as status_error:
                log.debug(f'unknown status error: {status_error}')
            raise ValueError
        try:
            pass
        except FileNotFoundError:
            return JobStatus.PENDING
