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


class AggregatorExtension(object):
    """Aggregator implementation consisting of hook programs."""

    def __init__(self, extension_root_dir):
        self.root = extension_root_dir

    def matches(self, core):
        return core.get_utils().call_hook(self.root, 'matches',
                                          core.get_source_directory())

    def dump(self, core):
        core.get_utils().call_hook(self.root, 'dump',
                                   core.get_source_directory())

    def get_info(self, core):
        info_file = os.path.join(self.root, 'data', 'info.json')
        if os.path.isfile(info_file):
            return json.load(open(info_file))
        else:
            return {'name': os.path.basename(self.root)}
