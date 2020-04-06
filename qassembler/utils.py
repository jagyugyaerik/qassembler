import json
import logging
import os
from typing import List, Dict, NamedTuple
from datetime import datetime
import json

from jinja2 import FileSystemLoader, Environment

import qassembler
from qassembler.config import CONTAINER_SHARED_VOLUME_PATH, OUTPUT_DIR_NAME, \
    ERROR_DIR_NAME, GOLDEN_BINARY_DIR_NAME, GOLDEN_REFERENCES_DIR_NAME, \
    BINARIES_DIR_NAME, REFERENCES_DIR_NAME, WORKING_DIRECTORY_PREFIX, \
    HOST_SHARED_VOLUME_PATH

log = logging.getLogger(__name__)

SgeJobParams = NamedTuple('SgeJobParams',
                          [('job_name', str),
                           ('shell_binary_path', str),
                           ('working_directory_path', str),
                           ('output_path', str),
                           ('error_path', str),
                           ('threads', str),
                           ('que', str),
                           ('golden_binary_path', str),
                           ('golden_reference_path', str),
                           ('binaries_path', str),
                           ('reference_path', str),
                           {'param_file_path', str},
                           ('pipeline', List[Dict[str, str]])])


def generate_job_name(prefix: str = 'sge') -> str:
    return '{}-{:%Y%m%d-%H%M%S-%f}'.format(prefix, datetime.now())


def render_qsub_template(params: SgeJobParams) -> str:
    # FIXME find a better way to get the package absolute path
    package_path = qassembler.__path__[0]  # type: ignore
    templates_folder = os.path.join(package_path, 'templates')
    file_loader = FileSystemLoader(searchpath=templates_folder)
    env = Environment(loader=file_loader)

    template = env.get_template('qsub_job.submit.j2')

    return template.render(params=params)


def create_qsub_job_file(filename: str, qsub_job: str) -> None:
    with open(filename, 'w') as qsub_file:
        qsub_file.writelines(qsub_job)


def create_directory_structure(location: str,
                               directories: List[str],
                               ) -> List[None]:
    return [os.mkdir(os.path.join(location, directory))  # type: ignore
            for directory in
            directories]


def generate_sge_job_params(pipeline: List[Dict[str, str]]) -> SgeJobParams:
    job_name = generate_job_name()
    working_directory_path = os.path.join(HOST_SHARED_VOLUME_PATH,
                                          WORKING_DIRECTORY_PREFIX, job_name)
    output_path = os.path.join(working_directory_path, OUTPUT_DIR_NAME)
    error_path = os.path.join(working_directory_path, ERROR_DIR_NAME)
    golden_binary_path = os.path.join(HOST_SHARED_VOLUME_PATH,
                                      GOLDEN_BINARY_DIR_NAME)
    golden_reference_path = os.path.join(HOST_SHARED_VOLUME_PATH,
                                         GOLDEN_REFERENCES_DIR_NAME)
    binaries_path = os.path.join(working_directory_path, BINARIES_DIR_NAME)
    reference_path = os.path.join(working_directory_path, REFERENCES_DIR_NAME)
    param_file_path = os.path.join(working_directory_path, 'param_file.json')
    return SgeJobParams(job_name=job_name,
                        shell_binary_path='/bin/bash',
                        working_directory_path=working_directory_path,
                        output_path=output_path,
                        error_path=error_path,
                        threads='1',
                        que='debug',
                        golden_binary_path=golden_binary_path,
                        golden_reference_path=golden_reference_path,
                        binaries_path=binaries_path,
                        reference_path=reference_path,
                        param_file_path=param_file_path,
                        pipeline=pipeline["pipeline"])  # type: ignore


def create_param_file(params: SgeJobParams) -> None:
    with open(os.path.join(params.param_file_path), 'w') as \
            param_file:
        param_file.writelines(json.dumps(params._asdict(), indent=4))
