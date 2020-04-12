import json
import json
import os
from datetime import datetime
from typing import List, Dict, NamedTuple

from qassembler.config import GOLDEN_BINARY_DIR_NAME, \
    GOLDEN_REFERENCES_DIR_NAME, \
    HOST_SHARED_VOLUME_PATH

SgeJobParams = NamedTuple('SgeJobParams',
                          [('job_name', str),
                           ('shell_binary_path', str),
                           ('threads', str),
                           ('que', str),
                           ('golden_binary_path', str),
                           ('golden_reference_path', str),
                           ('input_path', str),
                           ('pipeline', List[Dict[str, str]])])

Paths = NamedTuple('Paths',
                   [('working_directory_path', str),
                    ('output_path', str),
                    ('error_path', str),
                    ('binaries_path', str),
                    ('reference_path', str)])


def generate_job_name(prefix: str = 'sge') -> str:
    return '{}-{:%Y%m%d-%H%M%S-%f}'.format(prefix, datetime.now())


def create_directory_structure(location: str,
                               directories: List[str],
                               ) -> List[None]:
    os.mkdir(location)
    return [os.mkdir(os.path.join(location, directory))  # type: ignore
            for directory in
            directories]


def generate_sge_job_params(pipeline: List[Dict[str, str]],
                            input_path: str) -> SgeJobParams:
    job_name = generate_job_name()
    golden_binary_path = os.path.join(HOST_SHARED_VOLUME_PATH,
                                      GOLDEN_BINARY_DIR_NAME)
    golden_reference_path = os.path.join(HOST_SHARED_VOLUME_PATH,
                                         GOLDEN_REFERENCES_DIR_NAME)
    return SgeJobParams(job_name=job_name,
                        shell_binary_path='/bin/bash',
                        threads='1',
                        que='debug',
                        golden_binary_path=golden_binary_path,
                        golden_reference_path=golden_reference_path,
                        input_path=input_path,
                        pipeline=pipeline)  # type: ignore


def create_param_file(working_directory, params: SgeJobParams) -> None:
    with open(os.path.join(working_directory, 'param_file.json'), 'w') as \
            param_file:
        param_file.writelines(json.dumps(params._asdict(), indent=4))
