"""The crepuscular main command.
"""

import os

from crepuscular.core import StandardCore

# Command functions.  Each of these must accept the following arguments:
#   core: (crepuscular.core.Core)
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


# Build the set of commands from the command functions.
_commands = {}
for cmd in [help, inspect, list_aggregators]:
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
        core.get_logger().error('Unknown command: {}', argv[1])
        help(core)
        return 1

    command(core, argv[1:])

