"""Crepuscular core context.
"""

import json
import os
import subprocess
import sys
import yaml

from crepuscular import aggregator as agg
from crepuscular import actuator as acc
from crepuscular import proclib

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

    def info(self, fmt, *args, **kwargs):
        """Writes an info message to the user.

        Args:
            fmt: (basestring) A format string.  This will be called with the
                format method and the arguments passed in through 'args' or
                'kwargs'.
            args: List of arguments for format.
            kwargs: keyword arguments for format.
        """
        raise NotImplementedError()

    def warn(self, fmt, *args, **kwargs):
        """Writes a warning message to the user.

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

    def write_data(self, object):
        """Write a raw data object in pretty-printed yaml-like format."""
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

    def get_actuators(self):
        """Returns the list of available actuators."""
        raise NotImplementedError()

    def get_actuator(self, name):
        """Returns the actuator specified by 'name', None if none exists."""
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


def _write_dict(object, indent, written):
    sys.stdout.write('\n')
    for key, val in object.iteritems():
        sys.stdout.write('  ' * indent)
        sys.stdout.write('\033[36;40m{}: '.format(key))
        _write_object(val, indent + 1, written)


def _write_list(object, indent, written):
    sys.stdout.write('\n')
    for item in object:
        sys.stdout.write('  ' * indent)
        sys.stdout.write('\033[33;40m- ')
        _write_object(item, indent + 1, written)


def _write_object(object, indent, written):

    # Check for a cycle.
    obj_id = id(object)
    if obj_id in written:
        sys.stdout.write('\033[31;40mCYCLE!')
        return
    written.add(obj_id)

    # Write based on the specific object type.
    if isinstance(object, dict):
        _write_dict(object, indent, written)
    elif isinstance(object, list):
        _write_list(object, indent, written)
    else:
        sys.stdout.write('\033[37;40m{}\n'.format(object))

    written.remove(obj_id)


def _nl_terminate(line):
    """Make sure the line is newline terminate.

    Returns line, adding a newline to it if there isn't already one.

    Args:
        line: (str)

    Returns:
        (str)
    """
    if not line or line[-1] != '\n':
        line += '\n'
    return line


class StandardOutput(Output):
    """Standard implementation of Output.

    Writes colored text to stdout/stderr.
    """

    def error(self, fmt, *args, **kwargs):
        assert not (args and kwargs), (
            "error() method can accept either args or kwargs, but not both.")
        content = fmt.format(*args) if args else fmt.format(**kwargs)
        sys.stderr.write('\033[31;40m{}\033[m'.format(_nl_terminate(content)))

    def info(self, fmt, *args, **kwargs):
        assert not (args and kwargs), (
            "info() method can accept either args or kwargs, but not both.")
        content = fmt.format(*args) if args else fmt.format(**kwargs)
        sys.stderr.write('\033[32;40m{}\033[m'.format(_nl_terminate(content)))

    def warn(self, fmt, *args, **kwargs):
        assert not (args and kwargs), (
            "warn() method can accept either args or kwargs, but not both.")
        content = fmt.format(*args) if args else fmt.format(**kwargs)
        sys.stderr.write('\033[33;40m{}\033[m'.format(_nl_terminate(content)))

    def write_markdown(self, document):
        sys.stdout.write('\033[36;40m')
        sys.stdout.write(document)
        sys.stdout.write('\033[m')

    def write_row(self, *columns):
        sys.stdout.write('\033[37;40m{}\n'.format(' '.join(columns)))

    def write_data(self, object):
        _write_object(object, 0, set())


class StandardUtils(Utils):
    """Standard implementation of Utils."""

    def __init__(self, out):
        """
        Args:
            out: (Output)
        """
        self.out = out

    def call_hook(self, prefix, hook_name, *args):
        full_hook_name = os.path.join(prefix, 'bin', hook_name)
        return (os.path.exists(full_hook_name) and
                not subprocess.call([full_hook_name,] + list(args)))

    def get_hook_output(self, prefix, hook_name, *args, **kwargs):
        """Returns an object representing the output of a hook.

        The hook should produce a JSON document on standard output.

        Args:
            prefix: (str) the path to the aggregator or actuator directory
                corresponding to the current activity.
            hook_name: (str) simple hook name.
            *args: Hook arguments.
            **kwargs: keyword arguments:
                input: (str) If provided, this is the input to pass to the
                    hook.

        Returns:
            The python representation of the JSON document output by the hook
            or None if the hook doesn't exist.
        """

        full_hook_name = os.path.join(prefix, 'bin', hook_name)
        if not os.path.exists(full_hook_name):
            return None

        proc = subprocess.Popen([full_hook_name] + list(args),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE)
        output, err = proc.communicate(kwargs.get('input'))
        if err:
            self.out.error('Error output from {}:\n', full_hook_name)
            self.out.error('  {}', '  \n'.join(err.split('\n')))
        return json.loads(output)

    def run_hook(self, prefix, hook_name, *args, **kwargs):
        """Returns an object representing the final result of a hook.

        The hook should produce a JSON document on standard output.

        Args:
            prefix: (str) the path to the aggregator or actuator directory
                corresponding to the current activity.
            hook_name: (str) simple hook name.
            *args: Hook arguments.
            **kwargs: keyword arguments:
                input: (str) If provided, this is the input to pass to the
                    hook.

        Returns:
            The python representation of the JSON document output by the hook
            or None if the hook doesn't exist.
        """

        result = []
        def on_error(line):
            self.out.error('{}:{} {}', prefix, hook_name, line)

        def on_stdout_line(line):
            try:
                obj = json.loads(line)
                type = obj.get('type')
                if type == 'result':
                    result.append(obj)
                elif type == 'error':
                    self.out.error('{}', obj.get('error'))
                elif type == 'info':
                    self.out.info('{}', obj.get('message'))
                elif type == 'warn':
                    self.out.warn('{}', obj.get('message'))
                else:
                    self.out.error('Unrecognized object:\n')
                    self.out.write_data(obj)
            except ValueError:
                on_error(line)

        def on_pipe_error(pipe_name):
            self.out.error('Error reading from {} of hook {}:{}',
                           pipe_name, prefix, hook_name)

        full_hook_name = os.path.join(prefix, 'bin', hook_name)
        if not os.path.exists(full_hook_name):
            return None

        proclib.run(*[full_hook_name] + list(args),
                    stdin=kwargs.get('input'),
                    stdout_callback=on_stdout_line,
                    stderr_callback=on_error,
                    pipe_error_callback=on_pipe_error)

        return result[0] if result else None


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
        self.__actuators = None
        self.__utils = StandardUtils(self.__output)
        self.__source_dir = os.getcwd()

    def get_output(self):
        return self.__output

    def __build_plugin_list(self, plugin_type, plugin_factory):
        plugins = []
        type_dir = os.path.join(self.root, plugin_type)
        for dir in os.listdir(type_dir):
            full_name = os.path.join(type_dir, dir)
            plugins.append(plugin_factory(full_name))
        return plugins

    def get_aggregators(self):
        if self.__aggregators is None:
            self.__aggregators = self.__build_plugin_list(
                'aggregators', agg.AggregatorExtension)
        return self.__aggregators

    def get_actuators(self):
        if self.__actuators is None:
            self.__actuators = self.__build_plugin_list(
                'actuators', acc.ActuatorExtension)
        return self.__actuators

    def get_actuator(self, name):
        all = self.get_actuators()
        for actuator in all:
            if actuator.name == name:
                return actuator
        return None

    def get_ordered_aggregators(self):
        # Not really ordered at this time.
        return self.get_aggregators()

    def get_utils(self):
        return self.__utils

    def get_source_directory(self):
        return self.__source_dir
