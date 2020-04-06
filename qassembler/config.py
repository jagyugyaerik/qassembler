from . import __version__

QASSEMBLER_VERSION = __version__

CONTAINER_SHARED_VOLUME_PATH = '/shared-volume'
HOST_SHARED_VOLUME_PATH = '/home/erik/code/thesis/shared-volume'
CONTAINER_SSH_VOLUME_PATH = '/ssh-volume'
HOST_SSH_VOLUME_PATH = '/home/erik/code/thesis/shared-volume'
CONTAINER_PARAM_FILE_PATH = '/etc/params/param-file.json'

OUTPUT_DIR_NAME = 'output'
ERROR_DIR_NAME = 'error'
GOLDEN_BINARY_DIR_NAME = 'golden-binaries'
GOLDEN_REFERENCES_DIR_NAME = 'golden-references'
BINARIES_DIR_NAME = 'bin'
REFERENCES_DIR_NAME = 'ref'
WORKING_DIRECTORY_PREFIX = 'sge-jobs'
