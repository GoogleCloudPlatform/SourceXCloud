# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
        result = core.get_utils().run_hook(
            self.root, 'push', core.get_source_directory(), *args,
            input=json.dumps(image))
        return result
