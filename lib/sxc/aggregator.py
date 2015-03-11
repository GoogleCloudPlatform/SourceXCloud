"""The aggregator interface.
"""

import os
import json

class Aggregator(object):

    def matches(self, core):
        """Returns true if the aggregator matches the source directory.

        Args:
            core: (.core.Core)
        """
        raise NotImplementedError()

    def dump(self, core):
        """Dump debug information on the source directory.

        Args:
            core: (.core.Core)
        """
        raise NotImplementedError()

    def get_info(self, core):
        """Returns a dictionary object containing aggregator info.

        Keys include:
            name: (str) name of the aggregator.
            desc: (str) description of the aggregator.

        All keys should be treated as optional.
        """
        raise NotImplementedError()

    def generate_image(self, core):
        """Generate the SourceXCloud image files for the source directory.

        Args:
            core: (.core.Core)

        Returns:
            Python representation of the JSON image file.
        """
        raise NotImplementedError()


class AggregatorExtension(object):
    """Aggregator implementation consisting of hook programs."""

    def __init__(self, extension_root_dir):
        self.root = extension_root_dir

    def matches(self, core):
        return core.get_utils().call_hook(self.root, 'matches',
                                          core.get_source_directory())

    def dump(self, core):
        output = core.get_utils().get_hook_output(self.root, 'dump',
                                                  core.get_source_directory())
        core.get_output().write_data(output)

    def get_info(self, core):
        info_file = os.path.join(self.root, 'data', 'info.json')
        if os.path.isfile(info_file):
            return json.load(open(info_file))
        else:
            return {'name': os.path.basename(self.root)}

    def generate_image(self, core):
        output = core.get_utils().get_hook_output(self.root, 'genimage',
                                                  core.get_source_directory())
        if output is None:
            raise Exception('Unable to create image.')
        f = open(os.path.join(core.get_source_directory(), '.sxc'), 'w')
        json.dump(output, f)
        return output
