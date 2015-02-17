"""The actuator interface and implementations.
"""

import json
import os

class Actuator(object):

    def push(self, core, image, args):
        """Push an image to a target."""
        raise NotImplementedError()


class ActuatorExtension(Actuator):
    """Actuator extension consisting of hook programs."""

    def __init__(self, actuator_root_dir):
        self.root = actuator_root_dir
        self.name = os.path.basename(actuator_root_dir)

    def push(self, core, image, args):
        result = core.get_utils().get_hook_output(
            self.root, 'push', core.get_source_directory(), *args,
            input=json.dumps(image))
        return result
