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

"""Utilities for dealing with child processes."""

import fcntl
import os
import subprocess
import select


class _LineAccumulator(object):
    """Accumulates data and calls a callback for every line."""

    def __init__(self, lineCallback):
        self.__buffer = []
        self.__cb = lineCallback

    def add(self, data):
        # If there is a newline, call the callback on the data we've got so
        # far plus the newline.
        newline_pos = data.find('\n') + 1
        while newline_pos > 0:
            line = ''.join(self.__buffer) + data[:newline_pos]
            self.__buffer = []
            self.__cb(line)
            data = data[newline_pos:]
            newline_pos = data.find('\n') + 1

        # add whatever's leftover to the buffer.
        if data:
            self.__buffer.append(data)

    def finish(self):
        self.__cb(''.join(self.__buffer))
        self.__buffer = []


def _set_nonblocking(f):
    fd = f.fileno()
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

def run(*args, **kwargs):
    stdout_callback = kwargs.get('stdout_callback')
    stderr_callback = kwargs.get('stderr_callback')
    pipe_error = kwargs.get('pipe_error_callback')
    stdin = kwargs.get('stdin')

    # Define the accumulators to help us manage the process output.
    stdout_accumulator = _LineAccumulator(stdout_callback)
    stderr_accumulator = _LineAccumulator(stderr_callback)

    proc = subprocess.Popen(args,
                            stdout=subprocess.PIPE if stdout_callback else None,
                            stderr=subprocess.PIPE if stderr_callback else
                            None,
                            stdin=subprocess.PIPE if stdin else None)
    inputs = [proc.stdout, proc.stderr]
    outputs = [proc.stdin] if stdin else []

    # Make the inputs non-blocking
    if stdout_callback:
        _set_nonblocking(proc.stdout)
    if stderr_callback:
        _set_nonblocking(proc.stderr)

    while inputs or outputs:
        rdx, wrx, erx = select.select(inputs, outputs, inputs + outputs)

        # Remove any error pipes from consideration.
        for p in erx:
            if pipe_error:
                if p is proc.stderr:
                    name = 'stderr'
                elif p is proc.stdout:
                    name = 'stdout'
                elif p is proc.stdin:
                    name = 'stdin'
                pipe_error(name)
            inputs.remove(p)

        # Feed in the next chunk of standard input.
        if wrx:
            if stdin:
                wrx[0].write(stdin[:1024])
                wrx[0].flush()
                stdin = stdin[1024:]
            else:
                wrx[0].close()
                outputs = []

        # Read everything from the process.
        for p in rdx:
            data = os.read(p.fileno(), 1024)
            if p is proc.stdout:
                stdout_accumulator.add(data)
            else:
                stderr_accumulator.add(data)
            if not data:
                inputs.remove(p)

    stdout_accumulator.finish()
    stderr_accumulator.finish()
    return proc.wait()
