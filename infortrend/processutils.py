# Copyright (c) 2017 Infortrend Technology, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import six

from oslo_utils import strutils
from oslo_concurrency import processutils


def ssh_execute(ssh, cmd, process_input=None,
                addl_env=None, check_exit_code=True,
                binary=False, timeout=None):

    sanitized_cmd = strutils.mask_password(cmd)
    LOG.debug('Running cmd (SSH): %s', sanitized_cmd)
    if addl_env:
        raise InvalidArgumentError(_('Environment not supported over SSH'))

    if process_input:
        # This is (probably) fixable if we need it...
        raise InvalidArgumentError(_('process_input not supported over SSH'))

    stdin_stream, stdout_stream, stderr_stream = ssh.exec_command(
        cmd, timeout=timeout)
    channel = stdout_stream.channel

    # NOTE(justinsb): This seems suspicious...
    # ...other SSH clients have buffering issues with this approach
    stdout = stdout_stream.readlines()
    stderr = stderr_stream.readlines()

    stdin_stream.close()

    exit_status = channel.recv_exit_status()

    if six.PY3:
        # Decode from the locale using using the surrogateescape error handler
        # (decoding cannot fail). Decode even if binary is True because
        # mask_password() requires Unicode on Python 3
        stdout = os.fsdecode(stdout)
        stderr = os.fsdecode(stderr)
    stdout = strutils.mask_password(stdout)
    stderr = strutils.mask_password(stderr)

    # exit_status == -1 if no exit code was returned
    if exit_status != -1:
        LOG.debug('Result was %s' % exit_status)
        if check_exit_code and exit_status != 0:
            raise processutils.ProcessExecutionError(exit_code=exit_status,
                                                     stdout=stdout,
                                                     stderr=stderr,
                                                     cmd=sanitized_cmd)

    if binary:
        if six.PY2:
            # On Python 2, stdout is a bytes string if mask_password() failed
            # to decode it, or an Unicode string otherwise. Encode to the
            # default encoding (ASCII) because mask_password() decodes from
            # the same encoding.
            if isinstance(stdout, unicode):
                stdout = stdout.encode()
            if isinstance(stderr, unicode):
                stderr = stderr.encode()
        else:
            # fsencode() is the reverse operation of fsdecode()
            stdout = os.fsencode(stdout)
            stderr = os.fsencode(stderr)

    return (stdout, stderr)
