from . import __version__

QASSEMBLER_VERSION = __version__

CONTAINER_SHARED_VOLUME_PATH = '/shared-volume'
HOST_SHARED_VOLUME_PATH = '/home/erik/code/thesis/shared-volume'
CONTAINER_SSH_VOLUME_PATH = '/ssh-volume'
HOST_SSH_VOLUME_PATH = '/home/erik/code/thesis/ssh-volume'

PROJECT_PREFIX = 'sge-jobs'
PROJECT_DIRECTORIES = ('bin', 'ref', 'input', 'error', 'output')

GOLDEN_BINARY_DIR_NAME = 'golden_binary'
GOLDEN_REFERENCES_DIR_NAME = 'golden_references'
