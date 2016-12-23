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

from oslo_config import cfg
from oslo_log import log
from oslo_utils import excutils
from oslo_utils import importutils
import six

from manila.common import constants
from manila import exception
from manila.i18n import _, _LE, _LI, _LW
from manila.share import driver

LOG = log.getLogger(__name__)

infortrend_nas_opts = [
    cfg.StrOpt('infortrend_nas_ip',
               default='',
               help='Infortrend nas ip. '
               'It is the management ip.'),
    cfg.StrOpt('infortrend_nas_user',
               default='manila',
               help='Infortrend nas username. '
               'Default value is manila.'),
    cfg.StrOpt('infortrend_pools_name',
               default='',
               help='Infortrend nas pool name list. '
               'It is separated with comma.'),
    cfg.IntOpt('infortrend_cli_max_retries',
               default=5,
               help='Maximum retry time for cli. Default is 5.'),
    cfg.IntOpt('infortrend_cli_timeout',
               default=30,
               help='Default timeout for CLI in seconds. '
               'By Default, it is 30 seconds.'),
]

CONF = cfg.CONF
CONF.register_opts(infortrend_nas_opts)



class InfortrendCommonClass(object):

    def __init__(self, configuration=None):
    	self.configuration.append_config_values(infortrend_nas_opts)

        self.nas_ip = self.configuration.safe_get('infortrend_nas_ip')
        self.username = self.configuration.safe_get('infortrend_nas_user')
        self.password = self.configuration.safe_get('infortrend_nas_password')
        self.ssh_key = self.configuration.safe_get('infortrend_ssh_key')


	def do_setup(self):


    def check_for_setup_error(self):


    def _update_share_stats(self):

