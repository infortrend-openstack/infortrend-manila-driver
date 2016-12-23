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
"""
Infortrend NAS CLI factory.
"""

import os
import time
import six

from oslo_concurrency import processutils
from oslo_log import log
from manila.i18n import _LE
from manila import utils

LOG = log.getLogger(__name__)

DEFAULT_RETRY_TIME = 5


def retry_cli(func):
    def inner(self, *args, **kwargs):
        total_retry_time = self.cli_retry_time

        if total_retry_time is None:
            total_retry_time = DEFAULT_RETRY_TIME

        retry_time = 0
        while retry_time < total_retry_time:
            rc, out = func(self, *args, **kwargs)
            retry_time += 1

            if rc == 0:
                break

            LOG.error(_LE(
                'Retry %(retry)s times: %(method)s Failed '
                '%(rc)s: %(reason)s'), {
                    'retry': retry_time,
                    'method': self.__class__.__name__,
                    'rc': rc,
                    'reason': out})
        LOG.debug(
            'Method: %(method)s Return Code: %(rc)s '
            'Output: %(out)s', {
                'method': self.__class__.__name__, 'rc': rc, 'out': out})
        return rc, out
    return inner


