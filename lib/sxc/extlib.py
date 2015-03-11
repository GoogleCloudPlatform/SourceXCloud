"""Utilities useful for people writing extensions."""

import json
import os
import shutil
import sys
import tempfile


def send_object(obj):
    """Send an object back to the framework.

    Args:
        obj: An object that can be dumped using the json module.
            TODO: link to docs on valid message contents.
    """
    json.dump(obj, sys.stdout)
    sys.stdout.write('\n')
    sys.stdout.flush()


def error(message):
    """Write 'message' as an error message to the framework.

    Args:
        message: (str)
    """
    send_object({'type': 'error', 'error': message})


def info(message):
    """Write 'message' as an info message to the framework.

    Args:
        message: (str)
    """
    send_object({'type': 'info', 'message': message})


def warn(message):
    """Write 'message' as a warning message to the framework.

    Args:
        message: (str)
    """
    send_object({'type': 'warn', 'message': message})


class OutputRelay(object):
    """Tool to send the output of a child process to the framework.

    Sends stdout and stderr back to the process as 'info' and 'error'
    messages, respectfully.

    Usage:

        relay = OutputRelay('command')
        proclib.run('command', 'arg1', 'arg2',
                    stdout_callback=relay.stdout_callback,
                    stderr_callback=relay.stderr_callback)

    Ideally, extensions would do more sophisticated processing on the output
    of commands that they shell out to, but this makes for a nice default
    approach.
    """

    def __init__(self, prefix):
        """Constructor.

        Args:
            prefix: (str) prefix keyword to be injected at the beginning of
                all messages from the process.
        """
        self.__prefix = prefix

    def stdout_callback(self, line):
        info(line)

    def stderr_callback(self, line):
        error(line)


def stage_files(source_dir, image, staging_dir=None):
    """Stage files from the intermediate representation.

    Args:
        source_dir: (str) Source directory to copy files from.
        image: (object) The intermediate representation object.
            TODO: point to the spec.
        staging_dir: (str or None) If provided, this is the staging directory
            path to use. If not, a temporary staging directory will be
            constructed.  In the latter case, it is the responsibility of the
            caller to delete the staging directory upon completion.
    Returns:
        (str) the staging directory path.
    """
    if not staging_dir:
        staging_dir = tempfile.mkdtemp()

    for file in image['files']:
        full_name = os.path.join(staging_dir, 'app', file)

        # Create the directory if it doesn't exist.
        my_dir = os.path.dirname(full_name)
        if not os.path.exists(my_dir):
            os.makedirs(my_dir)

        # copy the file, resolving any symlinks.
        source_path = os.path.realpath(os.path.join(source_dir, file))
        if os.path.isfile(source_path):
            shutil.copyfile(source_path, full_name)

    return staging_dir
