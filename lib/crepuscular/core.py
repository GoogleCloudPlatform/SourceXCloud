"""Crepuscular core context.
"""

import os
import subprocess
import sys

from crepuscular import aggregator as agg

class Output(object):
    """Encapsulates all output to the user.

    This is similar to a logger interface with the subtle distinction that it is
    mainly for displaying semantically rich data to the user.
    """

    def error(self, fmt, *args, **kwargs):
        """Writes an error to the user.

        Args:
            fmt: (basestring) A format string.  This will be called with the
                format method and the arguments passed in through 'args' or
                'kwargs'.
            args: List of arguments for format.
            kwargs: keyword arguments for format.
        """
        raise NotImplementedError()

    def write_markdown(self, document):
        """Write a markdown document."""
        raise NotImplementedError()

    def write_row(self, *columns):
        """Write a row of tabular data."""
        raise NotImplementedError()


class Utils(object):
    """Encapsulates general purpose utility functions used by the system."""

    def call_hook(self, prefix, hook_name, *args):
        """Call the specified hook with arguments if it exists.

        If $prefix/bin/$hook_name exists, runs it with 'args'.

        Args:
            prefix: (str) The root directory of the bundle.
            hook_name: (str) The name of the hook program.
            *args: ([str, ...]) List of arguments to pass to the hook.

        Returns:
            (bool) True if the hook exists and was successful, false if not.
        """
        raise NotImplementedError()


class Core(object):
    """Encapsulates the crepusucular framework's core context information.

    Provides access to basic command configuration and libraries.
    """

    def get_output(self):
        """Returns the Output object for the system."""
        raise NotImplementedError()

    def get_aggregators(self):
        """Returns the list of available aggregators."""
        raise NotImplementedError()

    def get_ordered_aggregators(self):
        """Returns the list of aggregators in the order preferred by the user."""
        raise NotImplementedError()

    def get_utils(self):
        """Returns a Utils object for the system."""
        raise NotImplementedError()

    def get_source_directory(self):
        """Returns the path to the user's source directory."""
        raise NotImplementedError()


class StandardOutput(Output):
    """Standard implementation of Output.

    Writes colored text to stdout/stderr.
    """

    def error(self, fmt, *args, **kwargs):
        assert not (args and fmt), (
            "error() method can accept either args or kwargs, but not both.")
        content = fmt.format(*args) if args else fmt.format(**kwargs)
        sys.stderr.write('\033[31;40m{}\033[m'.format(content))

    def write_markdown(self, document):
        sys.stdout.write('\033[36;40m')
        sys.stdout.write(document)
        sys.stdout.write('\033[m')

    def write_row(self, *columns):
        sys.stdout.write('\033[37;40m{}\n'.format(' '.join(columns)))


class StandardUtils(Utils):
    """Standard implementation of Utils."""

    def call_hook(self, prefix, hook_name, *args):
        full_hook_name = os.path.join(prefix, 'bin', hook_name)
        return (os.path.exists(full_hook_name) and
                not subprocess.call([full_hook_name,] + list(args)))


class StandardCore(Core):
    """Standard implementation of Core."""

    def __init__(self, crepuscular_root):
        """Constructor.

        Args:
            crepuscular_root: (basestring) Root of the crepuscular distribution.
        """
        self.root = crepuscular_root
        self.__output = StandardOutput()
        self.__aggregators = None
        self.__utils = StandardUtils()
        self.__source_dir = os.getcwd()

    def get_output(self):
        return self.__output

    def get_aggregators(self):
        if self.__aggregators is None:
            self.__aggregators = []
            agg_dir = os.path.join(self.root, 'aggregators')
            for dir in os.listdir(agg_dir):
                full_name = os.path.join(agg_dir, dir)
                self.__aggregators.append(
                    agg.AggregatorExtension(full_name))
        return self.__aggregators

    def get_ordered_aggregators(self):
        # Not really ordered at this time.
        return self.get_aggregators()

    def get_utils(self):
        return self.__utils

    def get_source_directory(self):
        return self.__source_dir
