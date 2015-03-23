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

"""The SourceXCloud main command.
"""

import os

from sxc.core import StandardCore

# Command functions.  Each of these must accept the following arguments:
#   core: (sxc.core.Core)
#   args: ([str, ...]) Command arguments (excluding the command and
#       subcommand, so with "crep foo bar baz" args would be ['bar', 'baz']

def help(core, args=None):
    """Show this help message."""
    out = core.get_output()
    out.write_markdown('# Usage:\n')
    for cmd_name, func in _commands.iteritems():
        out.write_markdown('  {}:\n    {}\n'.format(cmd_name, func.__doc__))


def inspect(core, args):
    """Inspect the aggregator data for the current directory."""
    for aggregator in core.get_ordered_aggregators():
        if aggregator.matches(core):
            aggregator.dump(core)
            return
    else:
        core.get_output().error('Unknown directory type')


def list_aggregators(core, args):
    """List aggregators in the order that they will be applied."""
    out = core.get_output()
    for aggregator in core.get_ordered_aggregators():
        agg_info = aggregator.get_info(core)
        out.write_row(agg_info.get('name', ''), agg_info.get('desc', ''))


def genimage(core, args):
    """Generate the manifest for the source directory."""
    for aggregator in core.get_ordered_aggregators():
        if aggregator.matches(core):
            image = aggregator.generate_image(core)
            return image
    else:
        core.get_output().error('Unknown directory type')


def push(core, args):
    """<directory> <endpoint> [endpoint-args]
    Push the project in the source directory to the specified endpoint.
    """
    out = core.get_output()
    if len(args) < 2:
        out.write_markdown('push ' + push.__doc__)
        return
    image = genimage(core, args[0])
    actuator = core.get_actuator(args[1])
    if actuator is None:
        out.error('No actuator named {}'.format(args[1]))
        return

    # Invoke the actuator with the specified arguments.
    out.write_data(actuator.push(core, image, args[2:]))


# Build the set of commands from the command functions.
_commands = {}
for cmd in [help, inspect, list_aggregators, genimage, push]:
    _commands[cmd.__name__] = cmd


def main(argv):
    # We're temporarily assuming that extensions and this script are all in the
    # same tree.  This works for a demo but we'll need to change it long-term.
    root_dir = os.path.dirname(os.path.dirname(os.path.realpath(argv[0])))
    extensions_dir = os.path.join(root_dir, 'extensions')

    core = StandardCore(extensions_dir)
    if len(argv) < 2:
        help(core)
        return 1

    try:
        command = _commands[argv[1]]
    except KeyError as ex:
        core.get_output().error('Unknown command: {}', argv[1])
        help(core)
        return 1

    # Call the command with the remaining user-provided arguments.
    command(core, argv[2:])

